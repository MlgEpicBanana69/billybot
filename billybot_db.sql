CREATE DATABASE  IF NOT EXISTS `billybot_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `billybot_db`;
-- MySQL dump 10.13  Distrib 8.0.30, for Win64 (x86_64)
--
-- Host: localhost    Database: billybot_db
-- ------------------------------------------------------
-- Server version	8.0.30

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `shitposts_tbl`
--

DROP TABLE IF EXISTS `shitposts_tbl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shitposts_tbl` (
  `id` int NOT NULL AUTO_INCREMENT,
  `file_hash` varchar(64) NOT NULL,
  `file_extension_id` int NOT NULL,
  `submitter_id` varchar(18) NOT NULL,
  `description` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNIQUE_fileHash` (`file_hash`),
  UNIQUE KEY `UNIQUE_shitpostDescription` (`description`),
  KEY `FK_fileExtensionID_shitposts` (`file_extension_id`),
  KEY `FK_submitterID_shitposts` (`submitter_id`),
  CONSTRAINT `FK_fileExtensionID_shitposts` FOREIGN KEY (`file_extension_id`) REFERENCES `sp_file_extensions_tbl` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `FK_submitterID_shitposts` FOREIGN KEY (`submitter_id`) REFERENCES `sp_users_tbl` (`discord_user_id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sp_file_extensions_tbl`
--

DROP TABLE IF EXISTS `sp_file_extensions_tbl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_file_extensions_tbl` (
  `id` int NOT NULL AUTO_INCREMENT,
  `extension` varchar(4) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `extension_UNIQUE` (`extension`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sp_rating_tbl`
--

DROP TABLE IF EXISTS `sp_rating_tbl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_rating_tbl` (
  `entry` int NOT NULL AUTO_INCREMENT,
  `rating` tinyint NOT NULL,
  `submitter_id` varchar(18) NOT NULL,
  `shitpost_id` int NOT NULL,
  PRIMARY KEY (`entry`),
  UNIQUE KEY `rate_UNIQUE` (`submitter_id`,`shitpost_id`),
  KEY `FK_shitpostID_rating` (`shitpost_id`),
  CONSTRAINT `FK_shitpostID_rating` FOREIGN KEY (`shitpost_id`) REFERENCES `shitposts_tbl` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_submitterID_rating` FOREIGN KEY (`submitter_id`) REFERENCES `sp_users_tbl` (`discord_user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `legal_rating` CHECK (((`rating` >= 0) or (`rating` <= 100)))
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sp_shitposts_tags_tbl`
--

DROP TABLE IF EXISTS `sp_shitposts_tags_tbl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_shitposts_tags_tbl` (
  `entry` int NOT NULL AUTO_INCREMENT,
  `tag_id` int NOT NULL,
  `shitpost_id` int NOT NULL,
  PRIMARY KEY (`entry`),
  UNIQUE KEY `shitpost_tag_UNIQUE` (`tag_id`,`shitpost_id`),
  KEY `FK_shitpostID_shitpostingTags` (`shitpost_id`),
  CONSTRAINT `FK_shitpostID_shitpostingTags` FOREIGN KEY (`shitpost_id`) REFERENCES `shitposts_tbl` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_tagID_shitpostingTags` FOREIGN KEY (`tag_id`) REFERENCES `sp_tags_tbl` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=164 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `sp_shitposts_tags_view`
--

DROP TABLE IF EXISTS `sp_shitposts_tags_view`;
/*!50001 DROP VIEW IF EXISTS `sp_shitposts_tags_view`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `sp_shitposts_tags_view` AS SELECT 
 1 AS `tag_id`,
 1 AS `tag`,
 1 AS `shitpost_id`,
 1 AS `shitpost_description`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `sp_tags_tbl`
--

DROP TABLE IF EXISTS `sp_tags_tbl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_tags_tbl` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tag` varchar(256) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tag_UNIQUE` (`tag`)
) ENGINE=InnoDB AUTO_INCREMENT=147 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sp_user_privileges_tbl`
--

DROP TABLE IF EXISTS `sp_user_privileges_tbl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_user_privileges_tbl` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(16) NOT NULL,
  `owner` tinyint DEFAULT NULL,
  `administrator` tinyint NOT NULL,
  `submit` tinyint NOT NULL,
  `remove` tinyint NOT NULL,
  `rate` tinyint NOT NULL,
  `query` tinyint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  UNIQUE KEY `owner_UNIQUE` (`owner`),
  CONSTRAINT `administrator_bool` CHECK (((`administrator` = true) or (`administrator` = false))),
  CONSTRAINT `owner_oneOnly` CHECK (((`owner` = true) or (`owner` = NULL))),
  CONSTRAINT `query_bool` CHECK (((`query` = true) or (`query` = false))),
  CONSTRAINT `rate_bool` CHECK (((`rate` = true) or (`rate` = false))),
  CONSTRAINT `remove_bool` CHECK (((`remove` = true) or (`remove` = false))),
  CONSTRAINT `submit_bool` CHECK (((`submit` = true) or (`submit` = false)))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `sp_user_privileges_view`
--

DROP TABLE IF EXISTS `sp_user_privileges_view`;
/*!50001 DROP VIEW IF EXISTS `sp_user_privileges_view`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `sp_user_privileges_view` AS SELECT 
 1 AS `discord_user_id`,
 1 AS `id`,
 1 AS `name`,
 1 AS `owner`,
 1 AS `administrator`,
 1 AS `submit`,
 1 AS `remove`,
 1 AS `rate`,
 1 AS `query`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `sp_users_tbl`
--

DROP TABLE IF EXISTS `sp_users_tbl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_users_tbl` (
  `discord_user_id` varchar(18) NOT NULL,
  `privilege_id` int NOT NULL,
  PRIMARY KEY (`discord_user_id`),
  KEY `FK_privilegeID_users` (`privilege_id`),
  CONSTRAINT `FK_privilegeID_users` FOREIGN KEY (`privilege_id`) REFERENCES `sp_user_privileges_tbl` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `sp_shitposts_tags_view`
--

/*!50001 DROP VIEW IF EXISTS `sp_shitposts_tags_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`light`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `sp_shitposts_tags_view` AS select `sp_tags_tbl`.`id` AS `tag_id`,`sp_tags_tbl`.`tag` AS `tag`,`shitposts_tbl`.`id` AS `shitpost_id`,`shitposts_tbl`.`description` AS `shitpost_description` from ((`sp_shitposts_tags_tbl` join `shitposts_tbl` on((`sp_shitposts_tags_tbl`.`shitpost_id` = `shitposts_tbl`.`id`))) join `sp_tags_tbl` on((`sp_tags_tbl`.`id` = `sp_shitposts_tags_tbl`.`tag_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `sp_user_privileges_view`
--

/*!50001 DROP VIEW IF EXISTS `sp_user_privileges_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`light`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `sp_user_privileges_view` AS select `sp_users_tbl`.`discord_user_id` AS `discord_user_id`,`sp_user_privileges_tbl`.`id` AS `id`,`sp_user_privileges_tbl`.`name` AS `name`,`sp_user_privileges_tbl`.`owner` AS `owner`,`sp_user_privileges_tbl`.`administrator` AS `administrator`,`sp_user_privileges_tbl`.`submit` AS `submit`,`sp_user_privileges_tbl`.`remove` AS `remove`,`sp_user_privileges_tbl`.`rate` AS `rate`,`sp_user_privileges_tbl`.`query` AS `query` from (`sp_user_privileges_tbl` join `sp_users_tbl` on((`sp_users_tbl`.`privilege_id` = `sp_user_privileges_tbl`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-11-21 12:54:48
