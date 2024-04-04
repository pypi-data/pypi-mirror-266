import jwt
import concurrent.futures
import grpc
import time
import http.server
import urllib
import threading
import json

import ydb.iam

from yandex.cloud.iam.v1 import iam_token_service_pb2_grpc
from yandex.cloud.iam.v1 import iam_token_service_pb2

SERVICE_ACCOUNT_ID = "sa_id"
ACCESS_KEY_ID = "key_id"
PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC75/JS3rMcLJxv\nFgpOzF5+2gH+Yig3RE2MTl9uwC0BZKAv6foYr7xywQyWIK+W1cBhz8R4LfFmZo2j\nM0aCvdRmNBdW0EDSTnHLxCsFhoQWLVq+bI5f5jzkcoiioUtaEpADPqwgVULVtN/n\nnPJiZ6/dU30C3jmR6+LUgEntUtWt3eq3xQIn5lG3zC1klBY/HxtfH5Hu8xBvwRQT\nJnh3UpPLj8XwSmriDgdrhR7o6umWyVuGrMKlLHmeivlfzjYtfzO1MOIMG8t2/zxG\nR+xb4Vwks73sH1KruH/0/JMXU97npwpe+Um+uXhpldPygGErEia7abyZB2gMpXqr\nWYKMo02NAgMBAAECggEAO0BpC5OYw/4XN/optu4/r91bupTGHKNHlsIR2rDzoBhU\nYLd1evpTQJY6O07EP5pYZx9mUwUdtU4KRJeDGO/1/WJYp7HUdtxwirHpZP0lQn77\nuccuX/QQaHLrPekBgz4ONk+5ZBqukAfQgM7fKYOLk41jgpeDbM2Ggb6QUSsJISEp\nzrwpI/nNT/wn+Hvx4DxrzWU6wF+P8kl77UwPYlTA7GsT+T7eKGVH8xsxmK8pt6lg\nsvlBA5XosWBWUCGLgcBkAY5e4ZWbkdd183o+oMo78id6C+PQPE66PLDtHWfpRRmN\nm6XC03x6NVhnfvfozoWnmS4+e4qj4F/emCHvn0GMywKBgQDLXlj7YPFVXxZpUvg/\nrheVcCTGbNmQJ+4cZXx87huqwqKgkmtOyeWsRc7zYInYgraDrtCuDBCfP//ZzOh0\nLxepYLTPk5eNn/GT+VVrqsy35Ccr60g7Lp/bzb1WxyhcLbo0KX7/6jl0lP+VKtdv\nmto+4mbSBXSM1Y5BVVoVgJ3T/wKBgQDsiSvPRzVi5TTj13x67PFymTMx3HCe2WzH\nJUyepCmVhTm482zW95pv6raDr5CTO6OYpHtc5sTTRhVYEZoEYFTM9Vw8faBtluWG\nBjkRh4cIpoIARMn74YZKj0C/0vdX7SHdyBOU3bgRPHg08Hwu3xReqT1kEPSI/B2V\n4pe5fVrucwKBgQCNFgUxUA3dJjyMES18MDDYUZaRug4tfiYouRdmLGIxUxozv6CG\nZnbZzwxFt+GpvPUV4f+P33rgoCvFU+yoPctyjE6j+0aW0DFucPmb2kBwCu5J/856\nkFwCx3blbwFHAco+SdN7g2kcwgmV2MTg/lMOcU7XwUUcN0Obe7UlWbckzQKBgQDQ\nnXaXHL24GGFaZe4y2JFmujmNy1dEsoye44W9ERpf9h1fwsoGmmCKPp90az5+rIXw\nFXl8CUgk8lXW08db/r4r+ma8Lyx0GzcZyplAnaB5/6j+pazjSxfO4KOBy4Y89Tb+\nTP0AOcCi6ws13bgY+sUTa/5qKA4UVw+c5zlb7nRpgwKBgGXAXhenFw1666482iiN\ncHSgwc4ZHa1oL6aNJR1XWH+aboBSwR+feKHUPeT4jHgzRGo/aCNHD2FE5I8eBv33\nof1kWYjAO0YdzeKrW0rTwfvt9gGg+CS397aWu4cy+mTI+MNfBgeDAIVBeJOJXLlX\nhL8bFAuNNVrCOp79TNnNIsh7\n-----END PRIVATE KEY-----\n"  # noqa: E501
PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu+fyUt6zHCycbxYKTsxe\nftoB/mIoN0RNjE5fbsAtAWSgL+n6GK+8csEMliCvltXAYc/EeC3xZmaNozNGgr3U\nZjQXVtBA0k5xy8QrBYaEFi1avmyOX+Y85HKIoqFLWhKQAz6sIFVC1bTf55zyYmev\n3VN9At45kevi1IBJ7VLVrd3qt8UCJ+ZRt8wtZJQWPx8bXx+R7vMQb8EUEyZ4d1KT\ny4/F8Epq4g4Ha4Ue6OrplslbhqzCpSx5nor5X842LX8ztTDiDBvLdv88RkfsW+Fc\nJLO97B9Sq7h/9PyTF1Pe56cKXvlJvrl4aZXT8oBhKxImu2m8mQdoDKV6q1mCjKNN\njQIDAQAB\n-----END PUBLIC KEY-----\n"  # noqa: E501


def test_metadata_credentials():
    credentials = ydb.iam.MetadataUrlCredentials()
    raised = False
    try:
        credentials.auth_metadata()
    except Exception:
        raised = True

    assert raised


class IamTokenServiceForTest(iam_token_service_pb2_grpc.IamTokenServiceServicer):
    def Create(self, request, context):
        print("IAM token service request: {}".format(request))
        # Validate jwt:
        decoded = jwt.decode(
            request.jwt, key=PUBLIC_KEY, algorithms=["PS256"], audience="https://iam.api.cloud.yandex.net/iam/v1/tokens"
        )
        assert decoded["iss"] == SERVICE_ACCOUNT_ID
        assert decoded["aud"] == "https://iam.api.cloud.yandex.net/iam/v1/tokens"
        assert abs(decoded["iat"] - time.time()) <= 60
        assert abs(decoded["exp"] - time.time()) <= 3600

        response = iam_token_service_pb2.CreateIamTokenResponse(iam_token="test_token")
        response.expires_at.seconds = int(time.time() + 42)
        return response


class IamTokenServiceTestServer(object):
    def __init__(self):
        self.server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=2))
        iam_token_service_pb2_grpc.add_IamTokenServiceServicer_to_server(IamTokenServiceForTest(), self.server)
        self.server.add_insecure_port(self.get_endpoint())
        self.server.start()

    def stop(self):
        self.server.stop(1)
        self.server.wait_for_termination()

    def get_endpoint(self):
        return "localhost:54321"


class TestServiceAccountCredentials(ydb.iam.ServiceAccountCredentials):
    def _channel_factory(self):
        return grpc.insecure_channel(self._iam_endpoint)

    def get_expire_time(self):
        return self._expires_in - time.time()


class TestNebiusServiceAccountCredentials(ydb.iam.NebiusServiceAccountCredentials):
    def get_expire_time(self):
        return self._expires_in - time.time()


class NebiusTokenServiceHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        assert self.headers["Content-Type"] == "application/x-www-form-urlencoded"
        assert self.path == "/token/exchange"
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode("utf8")
        print("NebiusTokenServiceHandler.POST data: {}".format(post_data))
        parsed_request = urllib.parse.parse_qs(str(post_data))
        assert len(parsed_request["grant_type"]) == 1
        assert parsed_request["grant_type"][0] == "urn:ietf:params:oauth:grant-type:token-exchange"

        assert len(parsed_request["requested_token_type"]) == 1
        assert parsed_request["requested_token_type"][0] == "urn:ietf:params:oauth:token-type:access_token"

        assert len(parsed_request["subject_token_type"]) == 1
        assert parsed_request["subject_token_type"][0] == "urn:ietf:params:oauth:token-type:jwt"

        assert len(parsed_request["subject_token"]) == 1
        jwt_token = parsed_request["subject_token"][0]
        decoded = jwt.decode(
            jwt_token, key=PUBLIC_KEY, algorithms=["RS256"], audience="token-service.iam.new.nebiuscloud.net"
        )
        assert decoded["iss"] == SERVICE_ACCOUNT_ID
        assert decoded["sub"] == SERVICE_ACCOUNT_ID
        assert decoded["aud"] == "token-service.iam.new.nebiuscloud.net"
        assert abs(decoded["iat"] - time.time()) <= 60
        assert abs(decoded["exp"] - time.time()) <= 3600

        response = {
            "access_token": "test_nebius_token",
            "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "token_type": "Bearer",
            "expires_in": 42,
        }

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf8"))


class NebiusTokenServiceForTest(http.server.HTTPServer):
    def __init__(self):
        http.server.HTTPServer.__init__(self, ("localhost", 54322), NebiusTokenServiceHandler)

    def endpoint(self):
        return "http://localhost:54322/token/exchange"


def test_yandex_service_account_credentials():
    server = IamTokenServiceTestServer()
    credentials = TestServiceAccountCredentials(SERVICE_ACCOUNT_ID, ACCESS_KEY_ID, PRIVATE_KEY, server.get_endpoint())
    t = credentials.get_auth_token()
    assert t == "test_token"
    assert credentials.get_expire_time() <= 42
    server.stop()


def test_nebius_service_account_credentials():
    server = NebiusTokenServiceForTest()

    def serve(s):
        s.handle_request()

    serve_thread = threading.Thread(target=serve, args=(server,))
    serve_thread.start()

    credentials = TestNebiusServiceAccountCredentials(SERVICE_ACCOUNT_ID, ACCESS_KEY_ID, PRIVATE_KEY, server.endpoint())
    t = credentials.get_auth_token()
    assert t == "test_nebius_token"
    assert credentials.get_expire_time() <= 42

    serve_thread.join()
