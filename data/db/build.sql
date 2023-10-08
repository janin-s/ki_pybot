CREATE TABLE IF NOT EXISTS users (
    id integer NOT NULL,
    guild_id integer REFERENCES server_info(guild_id) ON DELETE SET NULL,
    display_name text,
    PRIMARY KEY(id, guild_id)
);

CREATE TABLE IF NOT EXISTS server_info (
    guild_id integer NOT NULL PRIMARY KEY,
    name text,
    main_channel integer,
    quote_channel integer,
    birthday_channel integer,
    reminder_channel integer,
    trading_channel integer
);

CREATE TABLE IF NOT EXISTS punish_times (
    user_id integer NOT NULL,
    guild_id integer NOT NULL,
    punish_time timestamp NOT NULL,
    PRIMARY KEY (user_id, guild_id),
    FOREIGN KEY (user_id, guild_id)
        REFERENCES users(id, guild_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS messages (
   	shorthand text not null,
	message text not null,
	guild_id integer
		references server_info (guild_id)
			on delete cascade,
	constraint messages_pk
		unique (shorthand, message, guild_id)
);

CREATE TABLE IF NOT EXISTS reminders (
    reminder_id integer,
    user_id integer NOT NULL,
    guild_id integer NOT NULL,
    time text NOT NULL,
    message text NOT NULL,
    mentions text NOT NULL,
    called boolean default false,
    PRIMARY KEY (reminder_id),
    FOREIGN KEY (user_id, guild_id)
        REFERENCES users(id, guild_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS roles (
    role_id integer NOT NULL,
    user_id integer NOT NULL,
    guild_id integer NOT NULL,
    PRIMARY KEY (role_id, user_id, guild_id),
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
    PRIMARY KEY (guild_id, user_id),
    FOREIGN KEY (user_id, guild_id)
        REFERENCES users (id, guild_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS birthdays (
    guild_id integer NOT NULL,
    user_id integer NOT NULL,
    month integer NOT NULL,
    day integer NOT NULL,
    PRIMARY KEY (user_id, guild_id),
    FOREIGN KEY (user_id, guild_id)
        REFERENCES users (id, guild_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trading_polls (
    poll_id integer,
    guild_id integer NOT NULL REFERENCES server_info (guild_id) ON DELETE CASCADE,
    start_time text NOT NULL,
    end_time text NOT NULL,
    asset1_id text NOT NULL,
    asset2_id text NOT NULL,
    channel_id integer,
    message_id integer,
    PRIMARY KEY (poll_id),
        FOREIGN KEY (guild_id)
        REFERENCES server_info(guild_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trading_votes (
    poll_id integer NOT NULL REFERENCES trading_polls (poll_id) ON DELETE CASCADE,
    user_id integer NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    asset_id text NOT NULL REFERENCES assets (id) ON DELETE CASCADE,
    PRIMARY KEY (poll_id, user_id)
);

CREATE TABLE IF NOT EXISTS assets (
    id text NOT NULL PRIMARY KEY,
    symbol text NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id integer PRIMARY KEY,
    guild_id integer NOT NULL references server_info (guild_id) ON DELETE CASCADE,
    channel_id integer NOT NULL,
    message_id integer NOT NULL,
    event_id integer NOT NULL,
    role_id integer NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    location TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rss_feed_last_entries (
    feed_id text PRIMARY KEY NOT NULL,
    last_entry_id text NOT NULL
);

INSERT OR IGNORE INTO server_info (guild_id, name, main_channel, quote_channel, birthday_channel, reminder_channel, trading_channel)
VALUES (705425948996272210, '10111011 Strassenbande', 705425949541269668, 705427122151227442, 705425949541269668, 705425949541269668, 705425949541269668);
INSERT OR IGNORE INTO messages (shorthand, message, guild_id)
VALUES  ('catanverbot', 'Bembl komm CS spielen!', 705425948996272210),
        ('chrissi', 'Chrissi ist so ein Lieber!', 705425948996272210),
        ('sev', '<:cursed:768963579973992468> https://de.wikihow.com/Einen-ganzen-Tag-lang-schweigen', 705425948996272210),
        ('janin', 'https://www.wikihow.com/Drop-Out-of-College', 705425948996272210),
        ('jan', 'Jan ist sehr nett und lieb!', 705425948996272210),
        ('lukas', 'https://de.wikihow.com/Mit-einer-geistig-behinderten-person-kommunizieren', 705425948996272210),
        ('nils', 'https://www.muenchen-heilpraktiker-psychotherapie.de/blog-2/selbstbewusstsein/10-anzeichen-dass-sie-zu-nett-sind-fuer-diese-welt.html', 705425948996272210),
        ('piep', 'piep piep, wir ham uns alle lieb! <:liebruh:731289435886583951>', 705425948996272210),
        ('amen', 'Vater unser da oben, wir wollen dich loben\nhier steht ganz viel dreck, mach die sünden weg\namen', 705425948996272210),
        ('gumo', '[$SENDER$] wünscht allen einen GuMo!', 705425948996272210),
        ('gumi', '[$SENDER$] wünscht allen einen Guten Mittach!', 705425948996272210),
        ('guab', '[$SENDER$] wünscht allen einen Guten Abend!', 705425948996272210),
        ('guna', '[$SENDER$] wünscht allen eine GuNa!', 705425948996272210),
        ('gugebu', 'Alles Gute [$MENTIONS$]!', 705425948996272210),
        ('bye', 'Bis denne Antenne!', 705425948996272210),
        ('bye', 'Ching Chang Ciao!', 705425948996272210),
        ('bye', 'Tschüsseldorf!', 705425948996272210),
        ('bye', 'Tschüßli Müsli!', 705425948996272210),
        ('bye', 'Bis Spätersilie!', 705425948996272210),
        ('bye', 'San Frantschüssko!', 705425948996272210),
        ('bye', 'Bis Baldrian!', 705425948996272210),
        ('bye', 'Bye mit Ei!', 705425948996272210),
        ('bye', 'Tschau mit au!', 705425948996272210),
        ('bye', 'Tschö mit ö!', 705425948996272210),
        ('bye', 'Hau Rheinwald!', 705425948996272210),
        ('bye', 'Schalömmchen!', 705425948996272210),
        ('bye', 'Schönes Knochenende!', 705425948996272210),
        ('bye', 'Schalömmchen!', 705425948996272210),
        ('bye', 'Tschüssikowski!', 705425948996272210),
        ('bye', 'Tüdelü in aller Früh!', 705425948996272210);
