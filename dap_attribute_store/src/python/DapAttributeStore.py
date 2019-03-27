class DapERNetwork(DapInterface.DapInterface):

    # configuration is a JSON deserialised config object.
    # structure is a map of tablename -> { fieldname -> type}

    class StoredFieldValue(object):
        def __init__(self, tfv: dap_update_pb2.DapUpdate.TableFieldValue = None):
            self.field_value = None
            self.field_type = None

            if update_pb:
                self.field_type, self.field_value = ProtoHelpers.decodeAttributeValueInfoToPythonType(upd.value)

        def match(self, operatorFactory, query_settings):
            f = operatorFactory.lookup(self.field_type, query_settings['operator'], query_settings['query_field_type'])
            if not f:
                return False
            return f(query_settings['query_field_value'], self.field_value)
            return True

    @has_logger
    def __init__(self, name, configuration):
        self.name = name

    def describe(self):
        result = dap_description_pb2.DapDescription()
        result.name = self.name

        star_table = result.table.add()
        star_table.name = '*'

        star_field = star_table.field.add()
        star_field.name = r'/them\..*/'
        star_field.type = '*'

        return result

    def prepareConstraint(self, proto: dap_interface_pb2.ConstructQueryConstraintObjectRequest) -> dap_interface_pb2.ConstructQueryMementoResponse:
        query_settings = {}

        target_field_name = proto.target_field_name
        if target_field_name[0:5] != 'them.':
            target_field_name = 'them.' + target_field_name

        query_settings['target_field_name'] = target_field_name
        query_settings['target_field_type'] = proto.target_field_type
        query_settings['operator'] = proto.operator
        query_settings['query_field_type'] = proto.query_field_type
        query_settings['query_field_value'] = DapInterface.decodeConstraintValue(proto.query_field_value)

        r = dap_interface_pb2.ConstructQueryMementoResponse()
        r.memento = json.dumps(query_settings).encode('utf8')
        r.success = True
        return r

    def test(row: dict, query_settings: dict) -> bool:
        target_field = row.get(j['target_field_name'], None)
        if target_field:
            return target_field.match(self.operatorFactory, query_settings)

    def execute(self, proto: dap_interface_pb2.DapExecute) -> dap_interface_pb2.IdentifierSequence:
        input_idents = proto.input_idents
        query_memento = proto.query_memento
        query_settings = json.loads(query_memento.memento.decode("utf-8"))

        r = dap_interface_pb2.IdentifierSequence()
        for table_name, table in self.store.items():
            if cores.originator:
                for (core_ident, agent_ident), row in table.items():
                    if test(row, j):
                        i = result.identifiers.add()
                        i.core = core_ident
                        i.agent = agent_ident
            else:
                for key in cores.identifiers:
                    core_ident, agent_ident = key.core, key.agent
                    row = table.get((core_ident, agent_ident), None)
                    if row != None and test(row, j):
                        i = result.identifiers.add()
                        i.core = core_ident
                        i.agent = agent_ident
        return r

    def update(self, update_data: dap_update_pb2.DapUpdate.TableFieldValue) -> dap_interface_pb2.Successfulness:
        r = dap_interface_pb2.Successfulness()
        r.success = True

        upd = update_data
        if upd:
            row_key = (upd.key.core, upd.key.agent)
            core_ident, agent_ident = row_key

            target_field_name = tfv.fieldname
            if target_field_name[0:5] != 'them.':
                target_field_name = 'them.' + target_field_name


            self.log.info("INSERT: core={}, agent={}".format(core_ident, agent_ident))

        return r

    def remove(self, remove_data: dap_update_pb2.DapUpdate) -> dap_interface_pb2.Successfulness:
        
