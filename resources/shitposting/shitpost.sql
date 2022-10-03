CREATE SCHEMA shitposting_db;

CREATE TABLE shitposting_db.tags_tbl(
	id INT NOT NULL AUTO_INCREMENT,
	tag VARCHAR(255) NOT NULL,
	PRIMARY KEY(id),
	UNIQUE KEY tag_UNIQUE (tag)
);

CREATE TABLE shitposting_db.user_privileges_tbl(
	name VARCHAR(16) NOT NULL,
	owner TINYINT NULL,
	administrator TINYINT NOT NULL,
	submit TINYINT NOT NULL,
	remove TINYINT NOT NULL,
	rate TINYINT NOT NULL,
	query TINYINT NOT NULL,
	PRIMARY KEY(name),
	UNIQUE KEY owner_UNIQUE (owner),
	CONSTRAINT owner_oneOnly CHECK (owner = TRUE OR owner = NULL),
	CONSTRAINT administrator_bool CHECK (administrator = TRUE OR administrator = FALSE),
	CONSTRAINT submit_bool CHECK (submit = TRUE OR submit = FALSE),
	CONSTRAINT remove_bool CHECK (remove = TRUE OR remove = FALSE),
	CONSTRAINT rate_bool CHECK (rate = TRUE OR rate = FALSE),
	CONSTRAINT query_bool CHECK (query = TRUE OR query = FALSE)
);

CREATE TABLE shitposting_db.users_tbl(
	discord_user_id VARCHAR(18) NOT NULL,
	privilege_name VARCHAR(16) NOT NULL,
	PRIMARY KEY(discord_user_id),
	CONSTRAINT FK_privilegeID_users
		FOREIGN KEY(privilege_name) REFERENCES shitposting_db.user_privileges_tbl(name)
		ON DELETE RESTRICT
		ON UPDATE CASCADE
);

CREATE TABLE shitposting_db.shitposts_tbl(
	id INT NOT NULL AUTO_INCREMENT,
	file BLOB NOT NULL,
	filename VARCHAR(45) NOT NULL,
	submitter_id VARCHAR(18) NOT NULL,
	description VARCHAR(255) NULL,
	PRIMARY KEY(id),
	CONSTRAINT FK_submitterID_shitposts
		FOREIGN KEY(submitter_id) REFERENCES shitposting_db.users_tbl(discord_user_id)
		ON DELETE NO ACTION
		ON UPDATE CASCADE
);

CREATE TABLE shitposting_db.shitposting_tags_tbl(
	entry INT NOT NULL AUTO_INCREMENT,
	tag_id INT NOT NULL,
	shitpost_id INT NOT NULL,
	PRIMARY KEY(entry),
	UNIQUE KEY shitpost_tag_UNIQUE (tag_id, shitpost_id),
	CONSTRAINT FK_tagID_shitpostingTags
		FOREIGN KEY(tag_id) REFERENCES shitposting_db.tags_tbl(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE,
	CONSTRAINT FK_shitpostID_shitpostingTags
		FOREIGN KEY(shitpost_id) REFERENCES shitposting_db.shitposts_tbl(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);

CREATE TABLE shitposting_db.rating_tbl(
	entry INT NOT NULL AUTO_INCREMENT,
	value TINYINT NOT NULL,
	submitter_id VARCHAR(18) NOT NULL,
	shitpost_id INT NOT NULL,
	PRIMARY KEY(entry),
	UNIQUE KEY rate_UNIQUE (submitter_id, shitpost_id),
	CONSTRAINT FK_submitterID_rating
		FOREIGN KEY(submitter_id) REFERENCES shitposting_db.users_tbl(discord_user_id)
		ON UPDATE CASCADE
		ON DELETE CASCADE,
	CONSTRAINT FK_shitpostID_rating
		FOREIGN KEY(shitpost_id) REFERENCES shitposting_db.shitposts_tbl(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE,
	CONSTRAINT value_legal_rate CHECK (value >= 0 OR value <= 100)
);

INSERT INTO shitposting_db.user_privileges_tbl
(name, owner, administrator, remove, submit, rate, query) VALUES
("owner", TRUE, TRUE, TRUE, TRUE, TRUE, TRUE),
("admin", NULL, TRUE, TRUE, TRUE, TRUE, TRUE),
("shitposter", NULL, FALSE, FALSE, TRUE, TRUE, TRUE),
("rater", NULL, FALSE, FALSE, FALSE, TRUE, TRUE),
("user", NULL, FALSE, FALSE, FALSE, FALSE, TRUE),
("banned", NULL, FALSE, FALSE, FALSE, FALSE, FALSE);
