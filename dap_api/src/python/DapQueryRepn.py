from abc import ABC
from abc import abstractmethod

from fetch_teams.oef_core_protocol import query_pb2

from dap_api.src.python import DapQueryRepnFromProtoBuf

class DapQueryRepn(object):

    class Branch(object):
        def __init__(self,
                combiner=None,
                **kwargs):
            self.leaves = []
            self.subnodes = []
            self.type = None
            self.combiner = combiner
            self.common_target_table_name = None
            self.common_dap_name = None
            self.name = "?"

        def Clear(self):
            self.leaves = []
            self.subnodes = []

        def printable(self):
            return "{} -- {} over {}, {}".format(
                self.name,
                self.combiner,
                self.common_target_table_name,
                self.common_dap_name
                )

        def print(self, depth=0):
            print(depth*"  ", self.printable())
            for n in self.subnodes:
                print("SUBNODE:")
                n.print(depth+1)
            for leaf in self.leaves:
                print((depth+1)*"  ", leaf.printable())

        def MergeDaps(self):
            dap_names = set(
                [
                    x.common_dap_name for x in self.subnodes
                ] + [
                    x.dap_name for x in self.leaves
                ]
            )
            self.common_dap_name = None
            if len(dap_names) == 1:
                self.common_dap_name = list(dap_names)[0]

        def Add(self, new_child):
            if isinstance(new_child, DapQueryRepn.Branch):
                self.subnodes.append(new_child)
            else:
                self.leaves.append(new_child)

    class Leaf(object):
        def __init__(self,
                operator=None,
                query_field_type=None,
                query_field_value=None,
                target_field_type=None,
                target_field_name=None,
                target_table_name=None,
                dap_name=None,
                **kwargs
                     ):
            self.operator          = operator

            self.query_field_value = query_field_value
            self.query_field_type  = query_field_type

            self.target_field_name = target_field_name
            self.target_field_type = target_field_type
            self.target_table_name = target_table_name

            self.dap_name          = dap_name
            self.name = "?"

        def printable(self):
            return "{} -- {}.{}.{} ({}) {} {} ({}) ==> {}".format(
                self.name,
                self.dap_name,
                self.target_table_name,
                self.target_field_name,
                self.target_field_type,
                self.operator,
                self.query_field_value,
                self.query_field_type,
                getattr(self, "row_processor", "None"),
                )

    class Visitor(ABC):
        def init(self):
            pass

        @abstractmethod
        def visitNode(self, node, depth):
            pass

        @abstractmethod
        def visitLeaf(self, leaf, depth):
            pass

    def print(self):
        self.root.print()

    def __init__(self):
        self.root = DapQueryRepn.Branch(combiner="all")

    def visit(self, visitor, node=None, depth=0):
        if not node:
            node = self.root
        if not node:
            return

        for subnode in node.subnodes:
            self.visit(visitor, subnode, depth+1)
        for leaf in node.leaves:
            visitor.visitLeaf(leaf, depth+1)
        visitor.visitNode(node, depth)

    def visitDescending(self, visitor, node=None, depth=0):
        if not node:
            node = self.root
        if not node:
            return

        if visitor.visitNode(node, depth):
            for subnode in node.subnodes:
                self.visit(visitor, subnode, depth+1)
            for leaf in node.leaves:
                visitor.visitLeaf(leaf, depth+1)

    def fromConstraintProtoList(self, queryFromProto, ce_list_pb):
        self.root.Clear()
        for ce_pb in ce_list_pb:
            self.root.Add(queryFromProto._CONSTRAINT_EXPR_toRepn(ce_pb))

    # passing in the embedding system is part of the hack SUPPORT_SINGLE_GLOBAL_EMBEDDING_QUERY
    def fromQueryProto(self, pb, embeddingInfo: object=None):
        try:
            ce_pb = pb.constraints
        except AttributeError:
            ce_pb = pb

        queryFromProto = DapQueryRepnFromProtoBuf.DapQueryRepnFromProtoBuf()
        self.fromConstraintProtoList(queryFromProto, ce_pb)

        # this is the SUPPORT_SINGLE_GLOBAL_EMBEDDING_QUERY hack to
        # put the global data_model into a constraint object.

        if pb.HasField('model'):
            x = queryFromProto.createEmbeddingMatchDataModel(embeddingInfo, pb.model)
            if x:
                self.root.Add(x)
        elif pb.HasField('description'):
            x = queryFromProto.createEmbeddingMatchString(embeddingInfo, pb.description)
            if x:
                self.root.Add(x)
