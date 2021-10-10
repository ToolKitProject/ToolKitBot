-- MariaDB dump 10.19  Distrib 10.6.4-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: ToolKit
-- ------------------------------------------------------
-- Server version	10.6.4-MariaDB
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO,ANSI' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table "Chats"
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "Chats" (
  "id" bigint(20) NOT NULL,
  "settings" longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid("settings")),
  "owner_id" bigint(20) NOT NULL,
  UNIQUE KEY "Chats_id_uindex" ("id"),
  KEY "Chats_Users_id_fk" ("owner_id"),
  CONSTRAINT "Chats_Users_id_fk" FOREIGN KEY ("owner_id") REFERENCES "Users" ("id") ON DELETE CASCADE
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "Logs"
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "Logs" (
  "log_id" bigint(20) NOT NULL AUTO_INCREMENT,
  "chat_id" bigint(20) NOT NULL,
  "executor_id" bigint(20) NOT NULL,
  "target_id" bigint(20) NOT NULL,
  "type" text COLLATE utf8mb4_unicode_ci NOT NULL,
  "date" datetime NOT NULL,
  PRIMARY KEY ("log_id"),
  UNIQUE KEY "Logs_log_id_uindex" ("log_id"),
  KEY "Logs_Chats_id_fk" ("chat_id"),
  KEY "Logs_Users_id_fk" ("executor_id"),
  KEY "Logs_Users_id_fk_2" ("target_id"),
  CONSTRAINT "Logs_Chats_id_fk" FOREIGN KEY ("chat_id") REFERENCES "Chats" ("id") ON DELETE CASCADE,
  CONSTRAINT "Logs_Users_id_fk" FOREIGN KEY ("executor_id") REFERENCES "Users" ("id") ON DELETE CASCADE,
  CONSTRAINT "Logs_Users_id_fk_2" FOREIGN KEY ("target_id") REFERENCES "Users" ("id") ON DELETE CASCADE
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "Messages"
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "Messages" (
  "user_id" bigint(20) NOT NULL,
  "chat_id" bigint(20) NOT NULL,
  "message_id" bigint(20) NOT NULL,
  "reply_message_id" bigint(20) DEFAULT NULL,
  "message" text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  "type" text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  "date" datetime NOT NULL,
  KEY "Messages_Chats_id_fk" ("chat_id"),
  KEY "Messages_Users_id_fk" ("user_id"),
  CONSTRAINT "Messages_Chats_id_fk" FOREIGN KEY ("chat_id") REFERENCES "Chats" ("id") ON DELETE CASCADE,
  CONSTRAINT "Messages_Users_id_fk" FOREIGN KEY ("user_id") REFERENCES "Users" ("id") ON DELETE CASCADE
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "Users"
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "Users" (
  "id" bigint(20) NOT NULL,
  "settings" longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid("settings")),
  "permissions" longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid("permissions")),
  UNIQUE KEY "Users_id_uindex" ("id")
);
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-10-10 11:23:18
