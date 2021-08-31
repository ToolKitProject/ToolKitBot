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
  "owner" bigint(20) NOT NULL,
  UNIQUE KEY "Chats_id_uindex" ("id"),
  KEY "Chats_Users_id_fk" ("owner"),
  CONSTRAINT "Chats_Users_id_fk" FOREIGN KEY ("owner") REFERENCES "Users" ("id")
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
  "message" text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  "type" text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  "date" datetime DEFAULT NULL,
  KEY "Messages_Chats_id_fk" ("chat_id"),
  KEY "Messages_Users_id_fk" ("user_id"),
  CONSTRAINT "Messages_Chats_id_fk" FOREIGN KEY ("chat_id") REFERENCES "Chats" ("id"),
  CONSTRAINT "Messages_Users_id_fk" FOREIGN KEY ("user_id") REFERENCES "Users" ("id")
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
  "reports" longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid("reports")),
  UNIQUE KEY "Users_id_uindex" ("id")
);
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-08-26 23:07:36
