CREATE SCHEMA "shitposting_db";

CREATE TABLE "shitposting_db"."users_tbl"(
	"discord_user_id" INT NOT NULL,
	"privilege_id" INT NOT NULL,
	PRIMARY KEY("discord_user_id")
	CONSTRAINT "privilege_id"
		FOREIGN KEY("privilege_id") REFERENCES "shitposting_db"."user_privleges_tbl"("id")
		ON DELETE RESTRICT
		ON UPDATE CASCADE
);

CREATE TABLE "shitposting_db"."shitposts_tbl"(
	"id" INT NOT NULL AUTO_INCREMENT,
	"file" BLOB NOT NULL,
	"filename" VARCHAR(45) NOT NULL,
	"submitter_id" INT NOT NULL,
	"description" VARCHAR(256) NULL,
	PRIMARY KEY("id"),
	CONSTRAINT "submitter_id"
		FOREIGN KEY("submitter_id") REFERENCES "shitposting_db"."users_tbl"("discord_user_id")
		ON DELETE NO ACTION
		ON UPDATE CASCADE
);

CREATE TABLE "shitposting_db"."tags_tbl"(
	"id" INT NOT NULL AUTO_INCREMENT,
	"tag" VARCHAR(45) NOT NULL,
	PRIMARY KEY("id"),
	UNIQUE INDEX "tag_UNIQUE" ("tag")
);

CREATE TABLE "shitposting_db"."shitposting_tags_tbl"(
	"entry" INT NOT NULL AUTO_INCREMENT,
	"tag_id" INT NOT NULL,
	"shitpost_id" INT NOT NULL,
	PRIMARY KEY("entry"),
	UNIQUE INDEX "shitpost_tag_UNIQUE" ("tag_id", "shitpost_id"),
	CONSTRAINT "tag_id"
		FOREIGN KEY("tag_id") REFERENCES "shitposting_db"."tags_tbl"("id")
		ON UPDATE CASCADE
		ON DELETE CASCADE
	CONSTRAINT "shitpost_id"
		FOREIGN KEY("shitpost_id") REFERENCES "shitposting_db"."shitposts_tbl"("id")
		ON UPDATE CASCADE
		ON DELETE CASCADE
);

CREATE TABLE "shitposting_db"."shitpost_rating_tbl"(
	"entry" INT NOT NULL AUTO_INCREMENT,
	"value" TINYINT NOT NULL,
	"submitter_id" INT NOT NULL,
	"shitpost_id", INT NOT NULL,
	PRIMARY KEY("entry")
	UNIQUE INDEX ("submitter_id", "shitpost_id")
	CONSTRAINT "submitter_id"
		FOREIGN KEY("submitter_id") REFERENCES "shitposting_db"."users_tbl"("id")
		ON UPDATE CASCADE
		ON DELETE CASCADE
	CONSTRAINT "shitpost_id"
		FOREIGN KEY("shitpost_id") REFERENCES "shitposting_db"."shitposts_tbl"("id")
		ON UPDATE CASCADE
		ON DELETE CASCADE
	CONSTRAINT "entry" CHECK ("entry" >= 0 OR "entry" <= 100)
);

CREATE TABLE "shitposting_db"."user_privileges_tbl"(
	"id" INT NOT NULL AUTO_INCREMENT,
	"name" VARCHAR(8) NOT NULL,
	"owner" TINYINT NOT NULL,
	"administrator" TINYINT NOT NULL,
	"submit" TINYINT NOT NULL,
	"remove" TINYINT NOT NULL,
	"rate" TINYINT NOT NULL,
	"query" TINYINT NOT NULL
	CONTSTRAINT "name" CHECK ("name" == TRUE OR "name" == FALSE)
	CONTSTRAINT "owner" CHECK (("owner" == TRUE OR "owner" == FALSE) AND ()) 
	CONTSTRAINT "administrator" CHECK ("administrator" == TRUE OR "administrator" == FALSE)
	CONTSTRAINT "submit" CHECK ("submit" == TRUE OR "submit" == FALSE)
	CONTSTRAINT "remove" CHECK ("remove" == TRUE OR "remove" == FALSE)
	CONTSTRAINT "rate" CHECK ("rate" == TRUE OR "rate" == FALSE)
	CONTSTRAINT "query" CHECK ("query" == TRUE OR "query" == FALSE)
);

INSERT INTO "shitposting_db"."user_privileges_tbl"
("name", "administrator", "submit", "remove", "rate", "query") VALUES
("admin", TRUE, TRUE, TRUE, TRUE, TRUE, TRUE),
("trusted", 
