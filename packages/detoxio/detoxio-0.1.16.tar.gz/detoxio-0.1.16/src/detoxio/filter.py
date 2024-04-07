import typing
import proto.dtx.messages.common.industry_pb2 as industry_pb2
import proto.dtx.messages.common.threat_pb2 as threat_pb2
import proto.dtx.services.prompts.v1.prompts_pb2 as prompts_pb2

# We cannot use typing.Union because Python <= 3.10 is
# broken with union of types. A lot of runtimes, including
# Kaggle and Colab are still on Python 3.10 so we have
# to support this hack for a while
SetParamMultiType = typing.TypeVar('T', str, int)

class PromptFilter:
    """
    The PromptFilter class provides an easy to use interface for building prompt filters.
    These filters can be used with detoxio.ai APIs to filter for specific prompts.
    """

    def __init__(self, industry: industry_pb2.IndustryDomain = None,
                 threat_class: threat_pb2.ThreatClass = None,
                 threat_category: threat_pb2.ThreatCategory = None,
                 labels: typing.Dict[str, str] = None):
        self.industry = industry
        self.threat_class = threat_class
        self.threat_category = threat_category
        self.labels = labels

        self.__filter = prompts_pb2.PromptGenerationFilterOption()

    def __filter__(self):
        """
        Get the internal prompt filter object. It is NOT recommended
        to directly mutate this object. This object is still exposed because
        protobuf client libraries evolve independently. If the protobuf client
        libraries are updated, you can access the internal filter object to
        access new fields without having to wait for this library to be updated.
        """
        return self.__filter

    def build(self) -> prompts_pb2.PromptGenerationFilterOption:
        """
        Build the prompt filter object.
        """
        if self.industry:
            self.__filter.industry = self.industry
        if self.threat_class:
            self.__filter.threat_class = self.threat_class
        if self.threat_category:
            self.__filter.threat_category = self.threat_category
        if self.labels:
            self.__filter.labels.update(self.labels)

        return self.__filter

    def set_industry(self, industry: SetParamMultiType):
        """
        Set the industry filter. You can supply a string such as "healthcare"
        which will be converted to "INDUSTRY_DOMAIN_HEALTHCARE" to lookup the
        protocol buffer enum value.
        """
        if isinstance(industry, str):
            industry = industry_pb2.IndustryDomain.Value(f"INDUSTRY_DOMAIN_{industry.upper()}")

        self.industry = industry
        return self

    def set_threat_class(self, threat_class: SetParamMultiType):
        """
        Set the threat class filter. You can supply a string such as "toxicity"
        which will be converted to "THREAT_CLASS_TOXICITY" to lookup the
        protocol buffer enum value.
        """
        if isinstance(threat_class, str):
            threat_class = threat_pb2.ThreatClass.Value(f"THREAT_CLASS_{threat_class.upper()}")

        self.threat_class = threat_class
        return self

    def set_threat_category(self, threat_category: SetParamMultiType):
        """
        Set the threat category filter. You can supply a string such as "jailbreak"
        which will be converted to "THREAT_CATEGORY_JAILBREAK" to lookup the
        protocol buffer enum value.
        """
        if isinstance(threat_category, str):
            threat_category = threat_pb2.ThreatCategory.Value(f"THREAT_CATEGORY_{threat_category.upper()}")

        self.threat_category = threat_category
        return self

    def set_labels(self, labels: typing.Dict[str, str]):
        """
        Set the labels filter. The labels filter is a key-value pair dictionary.
        """
        self.labels = labels
        return self

