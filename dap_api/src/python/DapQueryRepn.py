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
            self.name = "?"
            self.memento = None

            self.dap_names = set() # the set of names of all responding daps.
            self.dap_field_candidates = {}  # A map of name->field info for every responder.

        def Clear(self):
            self.leaves = []
            self.subnodes = []

        def Copy(self):
            return DapQueryRepn.Branch().fromProto(self.toProto())

        def printable(self):
            return "Branch {} -- \"{}\" over {} ({} children, {} leaves)".format(
                self.name,
                self.combiner,
                self.dap_names or "NO_COMMON_DAPS",
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
            dap_names = [
                    x.dap_names for x in self.subnodes
                ] + [
                    x.dap_names for x in self.leaves
                ]

            self.dap_names = dap_names[0]
            for n in dap_names[1:]:
                if n != self.dap_names:
                    self.dap_names = None
                    break

        def Add(self, new_child):
            if isinstance(new_child, DapQueryRepn.Branch):
                self.subnodes.append(new_child)
            else:
                self.leaves.append(new_child)

        def fromProto(self, pb):
            self.combiner = pb.operator
            self.dap_names = set(pb.dap_names)
            if pb.HasField('node_name'):
                self.name = pb.node_name

            self.leaves = [ DapQueryRepn.Leaf().fromProto(x) for x in  pb.constraints ]
            self.subnodes = [ DapQueryRepn.Branch().fromProto(x) for x in  pb.children ]
            return self

        def toProto(self):
            pb = dap_interface_pb2.ConstructQueryObjectRequest()
            pb.operator = self.combiner
            pb.dap_names.extend(list(self.dap_names))
            if self.name != None:
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
                #target_field_type=None,
                target_field_name=None,
                #target_table_name=None,
                dap_names=set(),
                dap_field_candidates=set(),
                **kwargs
                     ):
            self.operator          = operator

            self.query_field_value = query_field_value
            self.query_field_type  = query_field_type

            self.target_field_name = target_field_name
            #self.target_field_type = target_field_type
            #self.target_table_name = target_table_name

            self.dap_names = dap_names # the set of names of all responding daps.
            self.dap_field_candidates = dap_field_candidates  # A map of name->field info for every responder.
            self.name = "?"
            self.memento = None

        def toProto(self):
            pb = dap_interface_pb2.ConstructQueryConstraintObjectRequest()

            v = DapInterface.encodeConstraintValue(self.query_field_value, self.query_field_type)

            pb.query_field_value.CopyFrom(v)
            pb.node_name = self.name

            pb.operator          = self.operator
            pb.query_field_type  = self.query_field_type 
            pb.target_field_name = self.target_field_name
#            pb.target_field_type = self.target_field_type
#            pb.target_table_name = self.target_table_name
#            pb.dap_name          = self.dap_name
            if self.name != None:
                pb.node_name = self.name
            return pb

        def fromProto(self, pb):
            self.query_field_value = DapInterface.decodeConstraintValue(pb.query_field_value)
            self.operator          = pb.operator
            self.query_field_type  = pb.query_field_type
            self.target_field_name = pb.target_field_name
#            self.target_field_type = pb.target_field_type
#            self.target_table_name = pb.target_table_name
#            self.dap_name          = pb.dap_name
            if pb.HasField('node_name'):
                self.name = pb.node_name 
            return self

        def printable(self):
            return "Leaf {} -- daps={} {} {}  ({}) memento={}".format(
                self.name,
                self.dap_names,
                self.target_field_name,
                self.operator,
                self.query_field_value,
                self.query_field_type,
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
