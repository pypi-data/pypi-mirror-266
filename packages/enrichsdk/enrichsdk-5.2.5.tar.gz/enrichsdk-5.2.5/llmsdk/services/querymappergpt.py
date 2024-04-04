from fastapi.concurrency import run_in_threadpool

from .basegpt import BaseGPT
from .lib import *
from ..agents import LLMQueryMapper

logger = get_logger()


class QueryMapperGPT(BaseGPT):

    def __init__(self):
        super().__init__()
        self.name = "QueryMapperGPT"
        self.agentname = "querymappergpt"
        self.platform = "openai"
        self.namespace = "querymappergpt"

    async def get_llm_agent(self):
        querymapper_agent = LLMQueryMapper(name=self.agentname, platform=self.platform)

        logger.debug(f"Built agent for {self.agentname} and platform {self.platform}")

        return {
            "agent": querymapper_agent
        }

    def startup_extra_steps(self):
        spec = self.get_customer_profile_spec()

        self.agent.load_spec(spec=spec,
                             persist_directory=self.persist_directory,
                             index_name=self.index_name)

    def get_customer_profile_spec(self):
        # ruleset
        RULE__TIME_PERIOD = "TIME_PERIOD must be one of 'day', 'week', 'month', 'quarter', or 'year'. Previous three months should be interpreted as a quarter."
        RULE__COUNTRY = "All COUNTRY names must be converted to 2 character ISO country codes"
        RULE__METRIC = "METRIC must be one of 'NSV' or 'NR'"

        # setup the template spec
        default = {
            "name": "acme_gpt",
            "topk": 5,
            "context": [
                "these queries are about cross-border financial transactions (traffic) at a fintech company",
                "'financial institutions' are also known as banks",
                "GSV is a metric measuring sales volume",
                "NSV is a metric measuring sales volume",
                "NR is a metric measuring revenue"
            ],
            "templates": [
                {
                    "template": "how many partners went live over the past TIME_PERIOD",
                    "metadata": {
                        "key": "new_partners|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what new B2B partners went live over the past TIME_PERIOD",
                    "metadata": {
                        "key": "new_b2b_partners|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "which new source and/or destination countries have been launched this TIME_PERIOD",
                    "metadata": {
                        "key": "new_countries|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what is the trend of SOURCE_COUNTRY to DESTINATION_COUNTRY traffic over the last TIME_PERIOD",
                    "metadata": {
                        "key": "traffic_trend|SOURCE_COUNTRY|DESTINATION_COUNTRY|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD,
                            RULE__COUNTRY
                        ],
                    }
                },
                {
                    "template": "what is the list of all partners in COUNTRY",
                    "metadata": {
                        "key": "partners|COUNTRY",
                        "rules": [
                            RULE__COUNTRY
                        ],
                    }
                },
                {
                    "template": "what is the list of all source partners in COUNTRY",
                    "metadata": {
                        "key": "source_partners|COUNTRY",
                        "rules": [
                            RULE__COUNTRY
                        ],
                    }
                },
                {
                    "template": "what is the list of all destination partners in COUNTRY",
                    "metadata": {
                        "key": "dest_partners|COUNTRY",
                        "rules": [
                            RULE__COUNTRY
                        ],
                    }
                },
                {
                    "template": "what is the list of 'financial institutions' in COUNTRY",
                    "metadata": {
                        "key": "banks|COUNTRY",
                        "rules": [
                            RULE__COUNTRY
                        ],
                    }
                },
                {
                    "template": "how many senders and/or receivers have been serviced this TIME_PERIOD",
                    "metadata": {
                        "key": "active_sndrs_rcvrs|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what is the expected/projected sales metrics for this TIME_PERIOD",
                    "metadata": {
                        "key": "expected_sales|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what are the total sales for this TIME_PERIOD",
                    "metadata": {
                        "key": "current_sales|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what is the total revenue for this TIME_PERIOD",
                    "metadata": {
                        "key": "current_sales|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "rank destination countries based on METRIC from SOURCE_COUNTRY",
                    "metadata": {
                        "key": "rank_dest_countries_from_source_country|METRIC|SOURCE_COUNTRY",
                        "rules": [
                            RULE__METRIC,
                            RULE__COUNTRY
                        ],
                    }
                },
                {
                    "template": "rank source partners based on METRIC from SOURCE_COUNTRY",
                    "metadata": {
                        "key": "rank_source_partners_from_source_country|METRIC|SOURCE_COUNTRY",
                        "rules": [
                            RULE__METRIC,
                            RULE__COUNTRY
                        ],
                    }
                },
                {
                    "template": "what was the sales volumes generated from new partners this TIME_PERIOD",
                    "metadata": {
                        "key": "sales_new_partners|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "from how many countries were transactions received this TIME_PERIOD",
                    "metadata": {
                        "key": "source_countries|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "to how many countries were transactions sent this TIME_PERIOD",
                    "metadata": {
                        "key": "dest_countries|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what are the highlights of business performance this TIME_PERIOD vs. last TIME_PERIOD",
                    "metadata": {
                        "key": "highlights|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what are the destination countries which were inactive over the last TIME_PERIOD",
                    "metadata": {
                        "key": "inactive_destination_countries|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what are the destination partners which were inactive over the last TIME_PERIOD",
                    "metadata": {
                        "key": "inactive_destination_partners|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what are the source countries that were inactive over the last TIME_PERIOD",
                    "metadata": {
                        "key": "inactive_source_countries|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what are the source partners who were inactive over the last TIME_PERIOD",
                    "metadata": {
                        "key": "inactive_source_partners|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
            ]
        }

        return default


app = FastAPI()

##############################################
# Common
##############################################
add_show_cache(app)
add_show_health(app)
queryMapperGpt = QueryMapperGPT()
app.include_router(queryMapperGpt.router)

# # For IDE Debugging
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=10892)
