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
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shitposts_tbl`
--

LOCK TABLES `shitposts_tbl` WRITE;
/*!40000 ALTER TABLE `shitposts_tbl` DISABLE KEYS */;
INSERT INTO `shitposts_tbl` VALUES (6,'65be12bedafb89af39613123bb1278f029cabeebe7b787d365810dda9a0626eb',5,'238834017980514304','whitecat is not the father and does not need to pay child support whitedoable'),(7,'bd8768f061f5919973b249654b6f3656ee36141c2da3ceae70123ada19728be8',5,'238834017980514304','horizontally spinning stranger'),(8,'f52892b66218a5069d87e13bd26e0c9e72c322a857fb6ed3fbb84a928193641c',2,'238834017980514304','Let\'s Say, Hypothetically, I\'m a Barbie Girl'),(9,'042db74536f66ade492576f591740010bb64a1ee99a2ea9853b80162a36790fd',5,'238834017980514304','Cat saved from death by employees'),(10,'abca094b990c1ff761c8cb6ffe2f1dfd65d6828b52d13859896eba4eaf07c138',5,'238834017980514304','glorious stage housing an avocado'),(12,'544eaefc42687d9e597503431610672a60de608d49b2879ff48b46d790aeef9d',5,'238834017980514304','two cats spinnng a frying pan'),(13,'18ce19daef9236ca1213463676fa9ec0b14a5adf89a2396f9485ed7611600e30',5,'238834017980514304','no nut november is for beta ass mfs speech'),(14,'83b3b6c32ae07a5cfcb6fc22c17454888c5f7fea4d6b1e353406858244de5448',5,'238834017980514304','rocket league arial into twerking'),(16,'2131175b9860abc8fd60a5971e3cc5e45a2fdd17244ff7882dd39b67e3801479',5,'238834017980514304','cyberpunk edgerunners and the lego movie are identical'),(17,'ee953b33032efa5c4d90894a773ed6bc284bc1578a6bad3a7f0998c115612a06',5,'238834017980514304','mari doxes your ip'),(18,'976508d5a1c548253f757cba3e3585977648658abc403263966180602d747a3b',5,'238834017980514304','trollface cookies'),(19,'a99d5899df1547079cbffdf86a0d100339ab5ca96cab3dfdf83198a0547cc142',5,'238834017980514304','Zalenski requests 4 billion rockets to bomb donesk children'),(20,'1fe7358cc86bf6520c8ec8bff87b5f6cea4af17d4b874a192d9103f874b61283',5,'238834017980514304','nahida zhongli model swap'),(21,'223c7f333766d8b42f2b4e3280a4a90da5a49687252a4836a553b38f3df95552',5,'238834017980514304','Humans when a person is one year closer to death'),(22,'b394baca085a01eabf1fc7dc460b42862f303b98e48ebbfa31f4844a8fdd2c0e',3,'238834017980514304','art of basil as baller'),(23,'0d4a140d61943a7f9e72896c5b80ea96adc3c9f18f68b2d09b064adc0345ef96',5,'238834017980514304','gay king of the hill'),(24,'a21c9bd0cf1d14e1814624082fbe2f759fd4abc70fc9385f3adc2d66e93ed9ec',3,'238834017980514304','this old condom I found under my bed looks like the Mockingjay pin'),(25,'84f85e1e4bdbd7997e71655e4ee43b89ec520ae3c9517e259d5fa697e0f12b9e',5,'238834017980514304','the scenery sure is pleasent from my hot squid balloon'),(27,'9081d4b6d1fd3fbfc848926fde5f6a7bf1550e2dfd3bc0ae03aaf2343867725b',5,'238834017980514304','terraria developers the one piece is real'),(28,'5e4170875d8b3063380392b47473cfddea43d0eff111b1e54f31938b28548df7',5,'238834017980514304','teacher teaching how to prenounce moans'),(29,'e0cf4dada9c54ce8fb18c1c4a2f21ffd11b1b9dfb59039362860dccc13826788',5,'238834017980514304','pigeon dancing on a table with a group of people'),(30,'4b3a0e71086a09d6eaccab2e3b33fac184a2241a235021c1c318b13758953474',7,'238834017980514304','Installing VLC Media Player'),(31,'a2d34bc9fb9df0acef99e810872f53e8233fb1eb054badeb99b847e87bb255ad',5,'238834017980514304','pigeon refuses to eat seeds and runs into a furnace'),(32,'a4c2dbb907d9dc886b67126bd807836937de2f521358faadd2a11645a201bbc3',5,'238834017980514304','man sings to window opposum while feeding him with a fork'),(34,'38ce133233eaa0b61e0cafc69e77f089aee98dfe9a2ac446a627f6f40a02bf72',5,'238834017980514304','cirno plushie reads awooga horny sex comment'),(35,'e053c27044c70f58487a41aa7caafaca96f8c9a73bf57e022fcf022210fa1983',5,'238834017980514304','You\'ve been trolled'),(36,'678571f4fdb07d23d58cd539596f545a65a18fd9807afda855ff8aea16c5e05b',7,'238834017980514304','romanian anti air'),(37,'8e54230098ff1642d798c237d2ecf0bea06daa7e4681dd1a2d18ea1263c6b8e0',5,'238834017980514304','subway surfer in real life'),(38,'46ce87e3c2e42777c90c76bb980cbecef0f7b33e64f250d1a2a4b5692c3ddfd3',2,'238834017980514304','Let\'s say, hypothetically, that every time we touched'),(39,'8c97ceb6d83473e7c1bd19ba557b74abb2c8c20a8190f5c7bc9cf4b24bcfbe47',5,'238834017980514304','A bottle of soap getting grinded and ejaculating'),(40,'a6d2a1984f852bb1eb2de4b3b359f3b5f1687dc2f772e1d6f84f416c1adf97c2',5,'238834017980514304','woman cannot stop the hamburgers from calling her name'),(41,'da65a55d0ba3759845b1fd80be6ed92cf5fad3937b457b40b312a59245fde3c3',5,'238834017980514304','OH we\'re halfway there squidward on a chair'),(42,'81eff8aebffe1bbaa1f3e0893d32dfbbf4c0e320a227e6e680742babd5e2e25d',5,'238834017980514304','swat team raids house of two grandmas and then fixes the damages to the house'),(43,'b5058497cd6c4e3ebb6aca0d1608340be0d1bc6229491df71643fbbe9a876076',5,'238834017980514304','cat dancing with funny music'),(44,'6269046ea6dd900604732a0b8b1120685e413557d6f4a17d72e94a040c2ed19b',5,'238834017980514304','Turks finding out they are 1% Greek'),(45,'5a6ea0c282061b71cefa9d1b235c8b7519d167b233ad1ab8771a2bcb11890683',3,'238834017980514304','All new 25 gram benadryl made from 1200 pills'),(46,'8ee187a6a490a11f5ec6e8a7579138943fc71a149115e82fa20ee3dfdd648df9',5,'238834017980514304','mad funny slap walk nigga getting hard slapped from behind'),(47,'3d49d194647d97bbefb4ffb09af276dcc045d24c0c821f7377cfc9001bded4d6',5,'238834017980514304','nyan what you are reffering to as linux is actually gnu/linux'),(49,'5de3b794350a12bde7b991b34d91e62958661c86ce0583a7d0adf1f529a28f8e',5,'238834017980514304','kratos fury can only be satisfied by gay greek sex'),(52,'4fad9c26ab55c3de94e5a99b3619f3a638462019c1373f3e2c14b522464d03c1',2,'238834017980514304','May your Ls be many and your bitches few'),(53,'218820a086d5802f88b0c3423f4186c38ecbe31be89da21ce7b93b3955f499fc',5,'238834017980514304','Cheese thrown fast at crab in blue bin'),(54,'21637bfda1b3d2c42de67df943dcebd413848f8e91aec6179ba7f26c70650baf',1,'238834017980514304','important purchase today spamton plushie with boots'),(56,'c3c808dc7ce8678534f528d42d85bafe6e3eab50f6e8ef1fdec7110676f30b0f',5,'238834017980514304','what you are referring to as linux is actually gnu/linux');
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
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sp_rating_tbl`
--

LOCK TABLES `sp_rating_tbl` WRITE;
/*!40000 ALTER TABLE `sp_rating_tbl` DISABLE KEYS */;
INSERT INTO `sp_rating_tbl` VALUES (1,80,'238834017980514304',6),(22,90,'238834017980514304',7),(26,2,'238834017980514304',8);
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
) ENGINE=InnoDB AUTO_INCREMENT=146 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sp_shitposts_tags_tbl`
--

LOCK TABLES `sp_shitposts_tags_tbl` WRITE;
/*!40000 ALTER TABLE `sp_shitposts_tags_tbl` DISABLE KEYS */;
INSERT INTO `sp_shitposts_tags_tbl` VALUES (81,13,35),(15,15,7),(51,15,22),(14,17,6),(16,23,7),(63,24,27),(39,25,17),(77,26,34),(13,27,6),(24,28,10),(67,28,29),(72,28,31),(75,28,32),(59,29,25),(17,30,8),(87,30,38),(18,31,8),(88,31,38),(21,32,9),(22,33,9),(68,33,30),(20,34,9),(28,34,12),(99,34,43),(19,35,9),(105,35,45),(23,36,10),(56,37,24),(109,37,46),(107,38,46),(27,39,12),(50,40,22),(30,41,13),(29,43,13),(31,44,14),(34,47,16),(35,49,16),(37,50,17),(38,51,17),(36,52,17),(40,53,18),(80,53,35),(41,54,19),(42,55,19),(43,56,19),(46,63,20),(47,64,20),(45,65,20),(44,66,20),(48,68,21),(49,69,22),(52,70,22),(54,71,23),(53,72,23),(120,72,49),(55,73,24),(58,75,25),(93,75,41),(57,76,25),(62,77,27),(64,79,28),(79,79,34),(66,81,29),(71,81,31),(74,81,32),(65,82,29),(70,82,31),(69,83,30),(73,86,32),(78,87,34),(136,87,54),(76,88,34),(82,89,35),(94,89,41),(83,91,36),(84,92,36),(85,93,37),(86,94,37),(89,95,39),(90,96,39),(92,97,40),(91,98,40),(97,100,42),(95,102,42),(96,103,42),(98,104,42),(100,105,43),(102,106,44),(123,106,49),(101,107,44),(104,108,44),(103,109,44),(106,110,45),(112,111,47),(143,111,56),(111,112,47),(142,112,56),(108,115,46),(135,115,53),(118,116,49),(122,117,49),(121,118,49),(119,120,49),(140,121,56),(130,122,52),(131,123,52),(132,124,52),(133,125,52),(134,126,53),(138,127,54),(139,128,54),(137,130,54),(141,131,56);
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
) ENGINE=InnoDB AUTO_INCREMENT=133 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sp_tags_tbl`
--

LOCK TABLES `sp_tags_tbl` WRITE;
/*!40000 ALTER TABLE `sp_tags_tbl` DISABLE KEYS */;
INSERT INTO `sp_tags_tbl` VALUES (1,'8_BIT'),(100,'ADVERTISEMENT'),(64,'ALBEDOS_CREATIONS'),(2,'AMOGUS'),(81,'ANIMAL'),(3,'ARANARA'),(4,'BAD_APPLE'),(69,'BALLER_ROBLOX'),(70,'BASIL_OMORI'),(30,'BEN_SHAPIRO'),(5,'BETTER_CALL_SAUL'),(82,'BIRB'),(68,'BIRTHDAY_CELEBRATION'),(6,'BREAKING_BAD'),(37,'BRUH_MOMENT'),(91,'CANT_HAVE_SHIT_IN'),(7,'CARS_MOVIE'),(34,'CAT'),(8,'CBT'),(105,'CELEBRATION'),(61,'CHINA'),(88,'CIRNO_TOUHOU'),(83,'COMPUTER_IT_MEME'),(126,'CRAB'),(35,'CURSED'),(46,'CYBERPUNK'),(47,'CYBERPUNK_EDGERUNNERS'),(32,'DEATH'),(129,'DELTARUNE'),(51,'DOX'),(108,'DREAM_ON_MEME'),(127,'DRIP'),(110,'DRUGS'),(31,'FACTS_AND_LOGIC'),(60,'FRANCE'),(9,'FUMO'),(123,'GABRIEL_ULTRAKILL'),(72,'GAY'),(63,'GENSHIN_IMPACT'),(116,'GOD_OF_WAR'),(104,'GRANDMA'),(106,'GREEK'),(39,'HALF_LIFE'),(98,'HAMBURGER'),(73,'HUNGER_GAMES'),(117,'ICARUS'),(94,'IN_REAL_LIFE'),(10,'INTRODUCTION_MEME'),(50,'IP'),(57,'ISRAEL'),(71,'KING_OF_THE_HILL'),(78,'KIRIKO_OVERWATCH'),(120,'KRATOS_GOW'),(124,'L'),(11,'LEBRON_JAMES'),(112,'LINUX'),(12,'LOW_QUALITY'),(52,'MARI_OMORI'),(43,'MOTIVATIONAL'),(13,'MUSIC'),(14,'MY_CHILD_MEME'),(95,'MY_HONEST_REACTION'),(66,'NAHIDA_GENSHIN'),(111,'NERD_MEME'),(38,'NIGGA'),(125,'NO_BITCHES'),(41,'NO_NUT_NOVEMBER'),(33,'NSFW'),(96,'NUT'),(15,'OMORI'),(16,'ONE_PIECE'),(86,'OPOSSUM'),(17,'OSUGAME'),(80,'OVERWATCH'),(58,'PALESTINE'),(18,'PIRACY'),(87,'PLUSHIE'),(99,'POLITICS'),(109,'RACISM'),(19,'REGULAR_SHOW'),(103,'REPAIR_WORK'),(40,'ROBLOX'),(36,'ROBOTICS'),(44,'ROCKET_LEAGUE'),(92,'ROMANIA'),(56,'RUSSIA_UKRAINE_WAR'),(97,'SCHIZOPHRENIA'),(118,'SEX'),(79,'SEX_THEORY'),(89,'SONG'),(130,'SPAMTON_DELTARUNE'),(20,'SPEEDY_MCQUEEN'),(21,'SPINNING'),(29,'SPONGEBOB'),(76,'SPONGEBOB_SHOW'),(75,'SQUIDWARD'),(23,'STRANGER_OMORI'),(93,'SUBWAY_SURFER'),(102,'SWATTING'),(77,'TERRARIA'),(114,'TERRORISM'),(49,'THE_LEGO_MOVIE'),(24,'THE_ONE_PIECE_IS_REAL'),(25,'THREAT'),(26,'TOUHOU'),(53,'TROLLFACE'),(107,'TURKEY'),(128,'TWEET'),(55,'UKRAINE'),(122,'ULTRAKILL'),(62,'UNITED_KINGDOM'),(59,'UNITED_STATES'),(121,'UWU'),(115,'VIOLENCE'),(131,'VOICEOVER'),(27,'WHITECAT'),(28,'WONDER'),(54,'ZALENSKI'),(65,'ZHONGLI_GENSHIN');
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
INSERT INTO `sp_users_tbl` VALUES ('238834017980514304',1),('162503261864067073',3),('313330513987371009',3),('369393598153752576',3);
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

-- Dump completed on 2022-11-16 21:46:51
