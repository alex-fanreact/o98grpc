import time

import grpc

import other98_pb2
import other98_pb2_grpc

from google.protobuf import json_format
from bson.json_util import dumps

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import MessageToDict


# parsing to Document for mongoDb
def parse_to_document(message) -> dict:
    try:
        return MessageToDict(message)
    except:
        return None


# parsing from mongoDb cursor value to Message
def parse_post_view(raw_result) -> other98_pb2.PostView:
    try:
        return json_format.Parse(dumps(raw_result), other98_pb2.PostView(), ignore_unknown_fields=True)
    except:
        return None


def parse_post(raw_result) -> other98_pb2.Post:
    try:
        return json_format.Parse(dumps(raw_result), other98_pb2.Post(), ignore_unknown_fields=True)
    except:
        return None


def parse_profile(raw_result) -> other98_pb2.Profile:
    try:
        return json_format.Parse(dumps(raw_result), other98_pb2.Profile(), ignore_unknown_fields=True)
    except:
        return None


def parse_post_vote(raw_result) -> other98_pb2.PostVote:
    try:
        return json_format.Parse(dumps(raw_result), other98_pb2.PostVote(), ignore_unknown_fields=True)
    except:
        return None


def parse_comment_vote(raw_result) -> other98_pb2.CommentVote:
    try:
        return json_format.Parse(dumps(raw_result), other98_pb2.CommentVote(), ignore_unknown_fields=True)
    except:
        return None


# miscellaneous
current_milli_time = lambda: int(round(time.time() * 1000))