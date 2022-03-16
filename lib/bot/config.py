import os.path as path
import toml

class MissingKeyException(Exception):
    def __init__(self, *keys: str) -> None:
        super().__init__(*keys)


def _get_key(user, default, *path):
    if user is None and default is None:
        raise MissingKeyException(*path)
    elif len(path) == 0:
        return user if user is not None else default
    else:
        key = path[0]
        try:
            return _get_key(
                user[key] if user is not None and key in user else None,
                default[key] if default is not None and key in default else None,
                *(path[1:])
            )
        except MissingKeyException:
            raise MissingKeyException(*path)


class Config:
    def __init__(self, config_file: str):
        try:
            self.config = toml.load(open(config_file, mode="r"))
        except OSError as e:
            print(f"unable to open config file {config_file}: {e}")
        except (TypeError, toml.TomlDecodeError) as e:
            print(f"invalid config file: {e}")
        src_dir, _ = path.split(path.realpath(__file__))
        default_config_file = path.join(src_dir, "../../owo.toml")
        self.default_config = None
        if not path.samefile(config_file, default_config_file):
            try:
                self.default_config = toml.load(open(default_config_file, mode="r"))
            except OSError as e:
                print(f"unable to open default config file {default_config_file}: {e}")
            except (TypeError, toml.TomlDecodeError) as e:
                print(f"invalid default config file: {e}")

        self.command_prefix = str(self.get_key("command_prefix"))

        self.desc = str(self.get_key("desc"))

        self.owner_id = int(self.get_key("owner_id"))

        self.guild_id = int(self.get_key("guild_id"))

        self.discord_token = str(self.get_key("api_tokens", "discord"))

        self.twitter_api_key = str(self.get_key("api_tokens", "twitter_api_key"))
        self.twitter_api_secret = str(self.get_key("api_tokens", "twitter_api_secret"))
        self.twitter_bearer_token = str(self.get_key("api_tokens", "twitter_bearer_token"))

    def get_key(self, *path):
        return _get_key(self.config, self.default_config, *path)

    def has_user_supplied_toplevel_key(self, key):
        return key in self.config