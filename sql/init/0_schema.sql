-- SPDX-FileCopyrightText: 2018-2025 Joonas Rautiola <mail@joinemm.dev>
-- SPDX-License-Identifier: MPL-2.0
-- https://git.joinemm.dev/miso-bot
-- blacklists
CREATE TABLE IF NOT EXISTS blacklisted_guild (
    guild_id BIGINT,
    reason VARCHAR(1024),
    PRIMARY KEY (guild_id)
);

CREATE TABLE IF NOT EXISTS blacklisted_member (
    user_id BIGINT,
    guild_id BIGINT,
    PRIMARY KEY (user_id, guild_id)
);

CREATE TABLE IF NOT EXISTS blacklisted_user (
    user_id BIGINT,
    reason VARCHAR(1024),
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS blacklisted_channel (
    channel_id BIGINT,
    guild_id BIGINT,
    PRIMARY KEY (channel_id)
);

CREATE TABLE IF NOT EXISTS blacklisted_command (
    command_name VARCHAR(32),
    guild_id BIGINT,
    PRIMARY KEY (command_name, guild_id)
);

CREATE TABLE IF NOT EXISTS shadowbanned_user (
    user_id BIGINT,
    reason VARCHAR(1024),
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS lastfm_cheater (
    lastfm_username VARCHAR(32),
    flagged_on DATETIME,
    reason VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (lastfm_username)
);

CREATE TABLE IF NOT EXISTS lastfm_blacklist (
    user_id BIGINT,
    guild_id BIGINT,
    PRIMARY KEY (guild_id, user_id)
);

-- user data
CREATE TABLE IF NOT EXISTS notification (
    guild_id BIGINT,
    user_id BIGINT,
    keyword VARCHAR(64),
    times_triggered INT DEFAULT 0,
    PRIMARY KEY (guild_id, user_id, keyword)
);

CREATE TABLE IF NOT EXISTS custom_command (
    guild_id BIGINT,
    command_trigger VARCHAR(64),
    content VARCHAR(2000),
    added_on DATETIME,
    added_by BIGINT,
    PRIMARY KEY (guild_id, command_trigger)
);







CREATE TABLE IF NOT EXISTS artist_crown (
    guild_id BIGINT,
    user_id BIGINT,
    artist_name VARCHAR(256),
    cached_playcount INT,
    PRIMARY KEY (guild_id, artist_name)
);





CREATE TABLE IF NOT EXISTS lastfm_vote_setting (
    user_id BIGINT,
    is_enabled BOOLEAN DEFAULT TRUE,
    upvote_emoji VARCHAR(128) DEFAULT NULL,
    downvote_emoji VARCHAR(128) DEFAULT NULL,
    PRIMARY KEY (user_id)
);





CREATE TABLE IF NOT EXISTS user_profile (
    user_id BIGINT,
    description VARCHAR(500) DEFAULT NULL,
    background_url VARCHAR(255) DEFAULT NULL,
    background_color VARCHAR(6) DEFAULT NULL,
    border INT DEFAULT 0,
    theme ENUM('dark', 'light') DEFAULT 'dark',
    PRIMARY KEY (user_id)
);



-- settings
CREATE TABLE IF NOT EXISTS user_settings (
    user_id BIGINT,
    lastfm_username VARCHAR(64) DEFAULT NULL,
    sunsign VARCHAR(32) DEFAULT NULL,
    location_string VARCHAR(128) DEFAULT NULL,
    timezone VARCHAR(32) DEFAULT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id BIGINT,
    mute_role_id BIGINT DEFAULT NULL,
    levelup_messages BOOLEAN DEFAULT FALSE,
    autoresponses BOOLEAN DEFAULT TRUE,
    restrict_custom_commands BOOLEAN DEFAULT FALSE,
    delete_blacklisted_usage BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (guild_id)
);












CREATE TABLE IF NOT EXISTS voting_channel (
    guild_id BIGINT,
    channel_id BIGINT,
    voting_type ENUM('rating', 'voting'),
    PRIMARY KEY (channel_id)
);

CREATE TABLE IF NOT EXISTS muted_user (
    guild_id BIGINT,
    user_id BIGINT,
    channel_id BIGINT,
    unmute_on DATETIME DEFAULT NULL,
    PRIMARY KEY (guild_id, user_id)
);

-- caches
CREATE TABLE IF NOT EXISTS image_color_cache (
    image_hash VARCHAR(32),
    r TINYINT UNSIGNED NOT NULL,
    g TINYINT UNSIGNED NOT NULL,
    b TINYINT UNSIGNED NOT NULL,
    hex VARCHAR(6) NOT NULL,
    PRIMARY KEY (image_hash)
);

CREATE TABLE IF NOT EXISTS artist_image_cache (
    artist_name VARCHAR(255),
    image_hash VARCHAR(32),
    scrape_date DATETIME,
    PRIMARY KEY (artist_name)
);

CREATE TABLE IF NOT EXISTS album_image_cache (
    artist_name VARCHAR(255),
    album_name VARCHAR(255),
    image_hash VARCHAR(32),
    scrape_date DATETIME,
    PRIMARY KEY (artist_name, album_name)
);

CREATE TABLE IF NOT EXISTS marriage (
    first_user_id BIGINT UNIQUE,
    second_user_id BIGINT UNIQUE,
    marriage_date DATETIME,
    PRIMARY KEY (first_user_id, second_user_id)
);

CREATE TABLE IF NOT EXISTS stannable_artist (
    id INT NOT NULL AUTO_INCREMENT,
    artist_name VARCHAR(128),
    category VARCHAR(64) NOT NULL,
    UNIQUE(artist_name),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS colorizer_role (
    guild_id BIGINT,
    role_id BIGINT,
    color VARCHAR(7),
    PRIMARY KEY (guild_id, color)
);

CREATE TABLE IF NOT EXISTS colorizer_settings (
    guild_id BIGINT,
    baserole_id BIGINT,
    enabled BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (guild_id)
);
