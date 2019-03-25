from abc import ABC
from abc import abstractmethod
import json

from fetch_teams.oef_core_protocol import query_pb2

from dap_api.src.python import DapQueryRepnFromProtoBuf
from dap_api.src.protos import dap_interface_pb2
from dap_api.src.python import DapInterface

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
            self.query = None
            self.memento = None

        def Clear(self):
            self.leaves = []
            self.subnodes = []

        def Copy(self):
            return DapQueryRepn.Branch().fromProto(self.toProto())

        def printable(self):
            return "Branch {} -- \"{}\" over {}, {} ({} children, {} leaves)".format(
                self.name,
                self.combiner,
                self.common_target_table_name or "NO_TARGET_TABLE",
                self.common_dap_name or "NO_COMMON_DAP",
                len(self.subnodes),
                len(self.leaves),
                )

        def print(self, depth=0):
            print(depth*"  ", self.printable())
            for n in self.subnodes:
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

        def fromProto(self, pb):
            self.combiner = pb.operator
            self.common_target_table_name = pb.common_target_table_name
            self.common_dap_name = pb.common_dap_name
            self.name = pb.node_name

            self.leaves = [ DapQueryRepn.Leaf().fromProto(x) for x in  pb.constraints ]
            self.subnodes = [ DapQueryRepn.Branch().fromProto(x) for x in  pb.children ]

        def toProto(self):
            pb = dap_interface_pb2.ConstructQueryObjectRequest()
            pb.operator = self.combiner
            pb.common_target_table_name = self.common_target_table_name
            pb.common_dap_name = self.common_dap_name
            pb.node_name = self.name

            for leaf in self.leaves:
                new_leaf = pb.constraints.add()
                new_leaf.CopyFrom(leaf.toProto())

            for child in self.subnodes:
                new_child = pb.children.add()
                new_child.CopyFrom(child.toProto())

            return pb


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
            self.query = None
            self.memento = None

        def toProto(self):
                pb = dap_interface_pb2.ConstructQueryConstraintObjectRequest()

                v = DapInterface.encodeConstraintValue(self.query_field_value, self.query_field_type)

                pb.query_field_value.CopyFrom(v)
                pb.node_name = self.name

                pb.operator          = self.operator
                pb.query_field_type  = self.query_field_type 
                pb.target_field_name = self.target_field_name
                pb.target_field_type = self.target_field_type
                pb.target_table_name = self.target_table_name
                pb.dap_name          = self.dap_name

                return pb

        def fromProto(self, pb):
                self.query_field_value = DapInterface.decodeConstraintValue(pb.query_field_value)
                self.operator          = pb.operator
                self.query_field_type  = pb.query_field_type
                self.target_field_name = pb.target_field_name
                self.target_field_type = pb.target_field_type
                self.target_table_name = pb.target_table_name
                self.dap_name          = pb.dap_name
                return self

        def printable(self):
            return "Leaf {} -- {}.{}.{} ({}) {} {} ({}) ==> {}  {} {}".format(
                self.name,
                self.dap_name,
                self.target_table_name,
                self.target_field_name,
                self.target_field_type,
                self.operator,
                self.query_field_value,
                self.query_field_type,
                getattr(self, "row_processor", "None"),
                "QUERY" if self.query else "NO_QUERY",
                "MEM" if self.memento else "NO_MEM",
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
        print("DapQueryRepn_____________________________________")
        self.root.print()
        print("_________________________________________________")

    def __init__(self):
        self.root = DapQueryRepn.Branch(combiner="all")

    def Copy(self):
        return self.root.Copy()

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
                self.visitDescending(visitor, subnode, depth+1)
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
