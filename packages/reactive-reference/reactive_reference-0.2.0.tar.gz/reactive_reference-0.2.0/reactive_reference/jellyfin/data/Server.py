from dataclasses import dataclass


@dataclass
class Server:
    port: int
    url: str
    protocol: str
    api_key: str

    def __repr__(self):
        return f"Server({self.to_string()})"

    def to_string(self) -> str:
        return f"{self.protocol}{self.url}:{self.port}"
