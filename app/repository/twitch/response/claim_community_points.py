"""[
  {
    "data": {
      "claimCommunityPoints": {
        "claim": {
          "id": "1be09ea0-747e-431f-afdc-5339d86b2702",
          "multipliers": [],
          "pointsEarnedBaseline": 50,
          "pointsEarnedTotal": 50,
          "__typename": "CommunityPointsClaim"
        },
        "currentPoints": 65700,
        "error": null,
        "__typename": "ClaimCommunityPointsPayload"
      }
    },
    "extensions": {
      "durationMilliseconds": 61,
      "operationName": "ClaimCommunityPoints",
      "requestID": "01GEHY73J0DWFSAJGQ13CAERYF"
    }
  }
]"""
from model.base import ConfiguredBaseModel
from repository.twitch.response.base import Extensions


class CommunityPointsClaim(ConfiguredBaseModel):
    id: str
    points_earned_baseline: int
    points_earned_total: int
    __typename: str = "CommunityPointsClaim"


class ClaimCommunityPointsPayload(ConfiguredBaseModel):
    claim: CommunityPointsClaim
    current_points: int
    __typename: str = "ClaimCommunityPointsPayload"


class Data(ConfiguredBaseModel):
    claim_community_points: ClaimCommunityPointsPayload


class ClaimCommunityPoints(ConfiguredBaseModel):
    data: Data
    extensions: Extensions
