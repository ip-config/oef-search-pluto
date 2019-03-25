import abc
from abc import abstractmethod
from dap_api.src.protos import dap_description_pb2
from dap_api.src.protos import dap_interface_pb2

class DapMatcher(object):

    # Initialise this with the deserialised description

    def __init__(self, dap_name, structure_pb: dap_description_pb2.DapDescription):

        self.fields = {}
        self.dap_name = dap_name

        self.options = structure_pb.options

        for table_desc_pb in structure_pb.table:
            for field_description_pb in table_desc_pb.field:
                self.fields[field_description_pb.name] = {
                    'dap_name': self.dap_name,
                    'target_field_name': field_description_pb.name,
                    'target_table_name': table_desc_pb.name,
                    'target_field_type': field_description_pb.type,
                    'early': "early" in self.options,
                }

    def mergeMatchers(*matchers):

        the_dap_name = set([ x['dap_name'] for x in matchers ])
        the_target_table_name = set([ x['target_table_name'] for x in matchers ])
        the_early = set([ x['early'] for x in matchers ])

        if len(the_dap_name) > 1:
            return None
        if len(the_target_table_name) > 1:
            return None
        if len(the_early) > 1:
            return None

        return {
            'early': the_early[0],
            'dap_name': the_dap_name[0],
            'target_table_name': the_target_table_name[0],
            'target_field_name': None,
            'target_field_type': None,
        }

    def canMatch(self, target_field_name) -> dict:
        if "early" in self.options:
            return {
                'early': True,
                'dap_name': self.dap_name,
                'target_field_name': None,
                'target_table_name': None,
                'target_field_type': None,
            }
        return self.fields.get(target_field_name, None)
