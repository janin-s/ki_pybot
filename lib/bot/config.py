from os import path
import toml


class MissingKeyException(Exception):
    def __init__(self, *keys: str) -> None:
        super().__init__(*keys)


def _get_key(user, default, *path):
    if user is None and default is None:
        raise MissingKeyException(*path)
    if len(path) == 0:
        return user if user is not None else default

    key = path[0]
    try:
        return _get_key(
            user[key] if user is not None and key in user else None,
            default[key] if default is not None and key in default else None,
            *(path[1:])
        )
    except MissingKeyException as missing_key_ex:
        raise MissingKeyException(*path) from missing_key_ex


class Config:
    def __init__(self, config_file: str):
        try:
            self.config = toml.load(open(config_file, mode="r"))
        except OSError as ex:
            print(f"unable to open config file {config_file}: {ex}")
        except (TypeError, toml.TomlDecodeError) as ex:
            print(f"invalid config file: {ex}")
        src_dir, _ = path.split(path.realpath(__file__))
        default_config_file = path.join(src_dir, "../../config.toml")
        self.default_config = None
        if not path.samefile(config_file, default_config_file):
            try:
                self.default_config = toml.load(open(default_config_file, mode="r"))
            except OSError as ex:
                print(f"unable to open default config file {default_config_file}: {ex}")
            except (TypeError, toml.TomlDecodeError) as ex:
                print(f"invalid default config file: {ex}")

        self.command_prefix = str(self.get_key("command_prefix"))

        self.desc = str(self.get_key("desc"))

        self.owner_id = int(self.get_key("owner_id"))

        self.guild_id = int(self.get_key("guild_id"))

        self.discord_token = str(self.get_key("api_tokens", "discord"))

        self.news_api_key = str(self.get_key("api_tokens", "news_api_key"))
        self.weather_api_key = str(self.get_key("api_tokens", "weather_api_key"))
        self.twitter_api_key = str(self.get_key("api_tokens", "twitter_api_key"))
        self.twitter_api_secret = str(self.get_key("api_tokens", "twitter_api_secret"))
        self.twitter_bearer_token = str(self.get_key("api_tokens", "twitter_bearer_token"))

        self.alpaca_api_key_id = str(self.get_key("api_tokens", "alpaca_api_key_id"))
        self.alpaca_api_secret = str(self.get_key("api_tokens", "alpaca_api_secret"))

        self.openai_api_key = str(self.get_key("api_tokens", "openai_api_key"))
        self.openai_org_id = str(self.get_key("api_tokens", "openai_org_id"))

        self.brevo_api_key = str(self.get_key("api_tokens", "brevo_api_key"))

        self.leakcheck_api_key = str(self.get_key("api_tokens", "leakcheck_api_key"))

        self.claude_session_cookie = str(self.get_key("api_tokens", "claude_session_cookie"))

        self.letterxpress_user = str(self.get_key("api_tokens", "letterxpress_user"))
        self.letterxpress_token = str(self.get_key("api_tokens", "letterxpress_token"))

    def get_key(self, *path):
        return _get_key(self.config, self.default_config, *path)

    def has_user_supplied_toplevel_key(self, key):
        return key in self.config
