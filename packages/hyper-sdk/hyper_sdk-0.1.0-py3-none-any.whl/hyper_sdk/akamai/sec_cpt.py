import base64
import hashlib
import json
import os
import re
from collections import OrderedDict
from typing import List

sec_duration_expr = re.compile(r'data-duration=(\d+)')
sec_challenge_expr = re.compile(r'challenge="(.*?)"')
sec_page_expr = re.compile(r'src="(/_sec/cp_challenge/ak-challenge-\d+-\d+.htm)"')


class SecCptChallengeData:
    def __init__(self, token: str, timestamp: int, nonce: str, difficulty: int):
        self.token = token
        self.timestamp = timestamp
        self.nonce = nonce
        self.difficulty = difficulty


class SecCptChallenge:
    def __init__(self, duration: int, challenge_path: str, challenge_data: SecCptChallengeData):
        self.duration = duration
        self.challenge_path = challenge_path
        self.challenge_data = challenge_data

    @staticmethod
    def parse(html: str) -> 'SecCptChallenge':
        challenge_data = SecCptChallenge._parse_challenge_data(html)
        duration = SecCptChallenge._parse_duration(html)
        challenge_path = SecCptChallenge._parse_challenge_path(html)

        return SecCptChallenge(duration, challenge_path, challenge_data)

    @staticmethod
    def _parse_challenge_data(src: str) -> SecCptChallengeData:
        challenge_match = sec_challenge_expr.search(src)
        if not challenge_match:
            raise Exception("hyper-sdk: Challenge data not found.")

        decoded_challenge = base64.b64decode(challenge_match.group(1))
        challenge_data = json.loads(decoded_challenge)

        return SecCptChallengeData(
            challenge_data.get('token', ''),
            challenge_data.get('timestamp', 0),
            challenge_data.get('nonce', ''),
            challenge_data.get('difficulty', 0)
        )

    @staticmethod
    def _parse_duration(src: str) -> int:
        duration_match = sec_duration_expr.search(src)
        if not duration_match:
            raise Exception("hyper-sdk: Duration not found.")

        try:
            duration = int(duration_match.group(1))
        except ValueError as e:
            raise Exception(f"hyper-sdk: Invalid duration value: {e}")

        return duration

    @staticmethod
    def _parse_challenge_path(src: str) -> str:
        page_match = sec_page_expr.search(src)
        if not page_match:
            raise Exception("hyper-sdk: Challenge path not found.")

        return page_match.group(1)

    def generate_sec_cpt_payload(self, sec_cpt_cookie: str) -> str:
        sec, _, _ = sec_cpt_cookie.partition("~")

        answers = self._generate_sec_cpt_answers(sec)

        payload = OrderedDict([
            ("token", self.challenge_data.token),
            ("answers", answers)
        ])

        return json.dumps(payload)

    def update_sec_cpt_challenge_data(self, response_body: str):
        challenge_data = json.loads(response_body)
        self.challenge_data = SecCptChallengeData(
            challenge_data.get('token', ''),
            challenge_data.get('timestamp', 0),
            challenge_data.get('nonce', ''),
            challenge_data.get('difficulty', 0)
        )

    def _generate_sec_cpt_answers(self, sec: str) -> List[str]:
        answers = []
        difficulty = self.challenge_data.difficulty

        while True:
            answer = f"0.{os.urandom(8).hex()}"
            hash_input = f"{sec}{self.challenge_data.timestamp}{self.challenge_data.nonce}{difficulty}{answer}"

            output = 0
            for byte in hashlib.sha256(hash_input.encode('ascii')).digest():
                output = (output << 8) | byte
                output %= difficulty

            if output == 0:
                difficulty += 1
                answers.append(answer)

                if len(answers) == 10:
                    break
                continue

        return answers
