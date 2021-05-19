CREATE TABLE IF NOT EXISTS users (
    id integer NOT NULL,
    guild_id integer REFERENCES server_info(guild_id) ON DELETE SET NULL,
    display_name text,
    PRIMARY KEY(id, guild_id)
);

CREATE TABLE IF NOT EXISTS server_info (
    guild_id integer NOT NULL,
    name text,
    main_channel integer,
    quote_channel integer
);

CREATE TABLE IF NOT EXISTS punish_times (
    user_id integer NOT NULL,
    guild_id integer NOT NULL,
    punish_time timestamp NOT NULL,
    FOREIGN KEY (user_id, guild_id)
        REFERENCES users(id, guild_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS messages (
    msg_id integer NOT NULL,
    shorthand text NOT NULL,
    message text NOT NULL,
    guild_id integer REFERENCES server_info (guild_id) ON DELETE CASCADE,
    PRIMARY KEY (msg_id)
);

CREATE TABLE IF NOT EXISTS reminders (
    reminder_id integer NOT NULL,
    user_id integer NOT NULL,
    guild_id integer NOT NULL,
    time text NOT NULL,
    message text NOT NULL,
    PRIMARY KEY (reminder_id),
    FOREIGN KEY (user_id, guild_id)
        REFERENCES users(id, guild_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS roles (
    role_id integer NOT NULL,
    user_id integer NOT NULL,
    guild_id integer NOT NULL,
    PRIMARY KEY (role_id),
    FOREIGN KEY (user_id, guild_id)
        REFERENCES users(id, guild_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS counters (
    counter_name text,
    guild_id integer NOT NULL REFERENCES server_info (guild_id) ON DELETE CASCADE,
    value integer DEFAULT 0,
    description text,
    PRIMARY KEY (counter_name, guild_id)
);

CREATE TABLE IF NOT EXISTS votekick (
    guild_id integer NOT NULL,
    user_id integer NOT NULL,
    votes integer NOT NULL,
    FOREIGN KEY (guild_id, user_id)
        REFERENCES users (id, guild_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS birthdays (
    user_id integer NOT NULL,
    date text NOT NULL,
    FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
);