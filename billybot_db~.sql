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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shitposts_tbl`
--

LOCK TABLES `shitposts_tbl` WRITE;
/*!40000 ALTER TABLE `shitposts_tbl` DISABLE KEYS */;
INSERT INTO `shitposts_tbl` VALUES (6,'65be12bedafb89af39613123bb1278f029cabeebe7b787d365810dda9a0626eb',5,'238834017980514304','whitecat is not the father and does not need to pay child support whitedoable'),(7,'bd8768f061f5919973b249654b6f3656ee36141c2da3ceae70123ada19728be8',5,'238834017980514304','horizontally spinning stranger'),(8,'f52892b66218a5069d87e13bd26e0c9e72c322a857fb6ed3fbb84a928193641c',2,'238834017980514304','Let\'s Say, Hypothetically, I\'m a Barbie Girl'),(9,'042db74536f66ade492576f591740010bb64a1ee99a2ea9853b80162a36790fd',5,'238834017980514304','Cat saved from death by employees'),(10,'abca094b990c1ff761c8cb6ffe2f1dfd65d6828b52d13859896eba4eaf07c138',5,'238834017980514304','glorious stage housing an avocado');
/*!40000 ALTER TABLE `shitposts_tbl` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `sp_file_extensions_tbl`
--

LOCK TABLES `sp_file_extensions_tbl` WRITE;
/*!40000 ALTER TABLE `sp_file_extensions_tbl` DISABLE KEYS */;
INSERT INTO `sp_file_extensions_tbl` VALUES (7,'gif'),(4,'jpeg'),(3,'jpg'),(6,'mp3'),(5,'mp4'),(1,'png'),(2,'webm');
/*!40000 ALTER TABLE `sp_file_extensions_tbl` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sp_rating_tbl`
--

LOCK TABLES `sp_rating_tbl` WRITE;
/*!40000 ALTER TABLE `sp_rating_tbl` DISABLE KEYS */;
INSERT INTO `sp_rating_tbl` VALUES (1,80,'238834017980514304',6),(22,90,'238834017980514304',7);
/*!40000 ALTER TABLE `sp_rating_tbl` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sp_shitposts_tags_tbl`
--

LOCK TABLES `sp_shitposts_tags_tbl` WRITE;
/*!40000 ALTER TABLE `sp_shitposts_tags_tbl` DISABLE KEYS */;
INSERT INTO `sp_shitposts_tags_tbl` VALUES (15,15,7),(14,17,6),(16,23,7),(13,27,6),(24,28,10),(17,30,8),(18,31,8),(21,32,9),(22,33,9),(20,34,9),(19,35,9),(23,36,10);
/*!40000 ALTER TABLE `sp_shitposts_tags_tbl` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sp_tags_tbl`
--

LOCK TABLES `sp_tags_tbl` WRITE;
/*!40000 ALTER TABLE `sp_tags_tbl` DISABLE KEYS */;
INSERT INTO `sp_tags_tbl` VALUES (1,'8_BIT'),(2,'AMOGUS'),(3,'ARANARA'),(4,'BAD_APPLE'),(30,'BEN_SHAPIRO'),(5,'BETTER_CALL_SAUL'),(6,'BREAKING_BAD'),(7,'CARS_MOVIE'),(34,'CAT'),(8,'CBT'),(35,'CURSED'),(32,'DEATH'),(31,'FACTS_AND_LOGIC'),(9,'FUMO'),(10,'INTRODUCTION_MEME'),(11,'LEBRON_JAMES'),(12,'LOW_QUALITY'),(13,'MUSIC'),(14,'MY_CHILD_MEME'),(33,'NSFW'),(15,'OMORI'),(16,'ONE_PIECE'),(17,'OSUGAME'),(18,'PIRACY'),(19,'REGULAR_SHOW'),(36,'ROBOTICS'),(20,'SPEEDY_MCQUEEN'),(21,'SPINNING'),(29,'SPONGEBOB'),(23,'STRANGER_OMORI'),(24,'THE_ONE_PIECE_IS_REAL'),(25,'THREAT'),(26,'TOUHOU'),(27,'WHITECAT'),(28,'WONDER');
/*!40000 ALTER TABLE `sp_tags_tbl` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `sp_user_privileges_tbl`
--

LOCK TABLES `sp_user_privileges_tbl` WRITE;
/*!40000 ALTER TABLE `sp_user_privileges_tbl` DISABLE KEYS */;
INSERT INTO `sp_user_privileges_tbl` VALUES (1,'owner',1,1,1,1,1,1),(2,'admin',NULL,1,1,1,1,1),(3,'shitposter',NULL,0,1,0,1,1),(4,'rater',NULL,0,0,0,1,1),(5,'user',NULL,0,0,0,0,1),(6,'banned',NULL,0,0,0,0,0);
/*!40000 ALTER TABLE `sp_user_privileges_tbl` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `sp_users_tbl`
--

LOCK TABLES `sp_users_tbl` WRITE;
/*!40000 ALTER TABLE `sp_users_tbl` DISABLE KEYS */;
INSERT INTO `sp_users_tbl` VALUES ('238834017980514304',1),('162503261864067073',3);
/*!40000 ALTER TABLE `sp_users_tbl` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'billybot_db'
--

--
-- Dumping routines for database 'billybot_db'
--

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

-- Dump completed on 2022-11-09  7:17:44
