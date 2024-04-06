from antimatter.datatype.datatypes import Datatype
from antimatter.errors.errors import HandlerFactoryError
from antimatter.handlers.base import DataHandler
from antimatter.handlers.dict_list import DictList
from antimatter.handlers.dictionary import Dictionary
from antimatter.handlers.langchain import LangchainHandler
from antimatter.handlers.pandas_dataframe import PandasDataFrame
from antimatter.handlers.pytorch_dataloader import PytorchDataLoader
from antimatter.handlers.scalar import ScalarHandler


def factory(datatype: Datatype) -> DataHandler:
    """
    Factory returns an instance of a DataHandler matching the provided Datatype.

    :param datatype: The Datatype to get a handler for.
    :return:
    An implementation of the abstract DataHandler for handling data of the
    given type.
    """
    match datatype:
        case Datatype.Unknown:
            raise HandlerFactoryError("cannot create factory from 'Unknown' Datatype")
        case Datatype.Scalar:
            return ScalarHandler()
        case Datatype.Dict:
            return Dictionary()
        case Datatype.DictList:
            return DictList()
        case Datatype.PandasDataframe:
            return PandasDataFrame()
        case Datatype.PytorchDataLoader:
            return PytorchDataLoader()
        case Datatype.LangchainRetriever:
            return LangchainHandler()
