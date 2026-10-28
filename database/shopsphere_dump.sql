-- MySQL dump 10.13  Distrib 9.7.1, for Win64 (x86_64)
--
-- Host: localhost    Database: shopsphere
-- ------------------------------------------------------
-- Server version	9.7.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '351d6b62-842a-11f1-892b-b8f7759eda2b:1-4078';

--
-- Current Database: `shopsphere`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `shopsphere` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `shopsphere`;

--
-- Table structure for table `addresses`
--

DROP TABLE IF EXISTS `addresses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `addresses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `label` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `full_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `line1` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `line2` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `city` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `state` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `postal_code` varchar(12) COLLATE utf8mb4_unicode_ci NOT NULL,
  `country` varchar(60) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_default` tinyint(1) DEFAULT NULL,
  `is_deleted` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_addresses_user_id` (`user_id`),
  CONSTRAINT `addresses_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `addresses`
--

LOCK TABLES `addresses` WRITE;
/*!40000 ALTER TABLE `addresses` DISABLE KEYS */;
INSERT INTO `addresses` VALUES (1,9,'Home','shipping','Ravi Customer','9876543210','Plot 12, Road No 3','Banjara Hills','Hyderabad','Telangana','500034','India',0,0,'2026-10-28 09:00:49'),(2,9,'Office','shipping','Ravi Kumar','9876543210','Cyber Towers, Hitech City',NULL,'Hyderabad','Telangana','500081','India',1,0,'2026-10-28 10:39:32');
/*!40000 ALTER TABLE `addresses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('0001');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attributes`
--

DROP TABLE IF EXISTS `attributes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attributes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `data_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `allowed_values` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `attributes_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attributes`
--

LOCK TABLES `attributes` WRITE;
/*!40000 ALTER TABLE `attributes` DISABLE KEYS */;
INSERT INTO `attributes` VALUES (1,'Color','choice','Black,White,Blue,Red',NULL),(2,'RAM (GB)','number',NULL,2);
/*!40000 ALTER TABLE `attributes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `actor_id` int DEFAULT NULL,
  `action` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `entity` varchar(60) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `entity_id` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `old_value` json DEFAULT NULL,
  `new_value` json DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_audit_logs_actor_id` (`actor_id`),
  KEY `ix_audit_logs_created_at` (`created_at`),
  KEY `ix_audit_logs_entity` (`entity`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_logs`
--

LOCK TABLES `audit_logs` WRITE;
/*!40000 ALTER TABLE `audit_logs` DISABLE KEYS */;
INSERT INTO `audit_logs` VALUES (1,2,'user.create','user','12','null','{\"role\": \"support_agent\", \"email\": \"agent950@shopsphere.com\"}','2026-10-28 10:39:32'),(2,2,'user.role_change','user','12','{\"role\": \"support_agent\"}','{\"role\": \"order_manager\"}','2026-10-28 10:39:32'),(3,2,'user.status_change','user','12','{\"status\": \"active\"}','{\"status\": \"suspended\"}','2026-10-28 10:39:32'),(4,3,'category.create','category','5','null','{\"name\": \"Laptops 125\"}','2026-10-28 10:39:33'),(5,3,'product.create','product','4','null','{\"sku\": \"DELL-INS-809\", \"price\": \"55000\"}','2026-10-28 10:39:34'),(6,3,'product.price_change','product','4','{\"base\": \"55000.00\", \"sale\": null}','{\"base\": \"54000\", \"sale\": \"49999\"}','2026-10-28 10:39:34'),(7,4,'inventory.add','inventory','7','{\"quantity\": 0}','{\"quantity\": 25}','2026-10-28 10:39:34'),(8,4,'transfer.dispatch','transfer','1','null','{\"qty\": 3}','2026-10-28 10:39:35'),(9,4,'transfer.receive','transfer','1','null','{\"qty\": 3}','2026-10-28 10:39:35'),(10,NULL,'order.status_change','order','1','{\"status\": \"pending\"}','{\"status\": \"confirmed\"}','2026-10-28 10:39:37'),(11,8,'refund.processed','refund','1','null','{\"amount\": \"100.00\", \"status\": \"succeeded\"}','2026-10-28 10:39:38'),(12,5,'order.status_change','order','1','{\"status\": \"confirmed\"}','{\"status\": \"processing\"}','2026-10-28 10:39:38'),(13,5,'order.status_change','order','1','{\"status\": \"processing\"}','{\"status\": \"shipped\"}','2026-10-28 10:39:38'),(14,5,'shipment.dispatched','shipment','1','null','{\"order\": \"ORD-261028-J09E4XCN\"}','2026-10-28 10:39:38'),(15,7,'order.status_change','order','1','{\"status\": \"shipped\"}','{\"status\": \"delivered\"}','2026-10-28 10:39:39'),(16,5,'return.approved','return','1','null','{\"note\": null}','2026-10-28 10:39:40'),(17,5,'refund.processed','refund','2','null','{\"amount\": \"15043.82\", \"status\": \"succeeded\"}','2026-10-28 10:39:40'),(18,2,'supplier.status','supplier','2','{\"status\": \"pending\"}','{\"status\": \"approved\"}','2026-10-28 10:39:41'),(19,8,'invoice.create','supplier_invoice','1','null','{\"po_id\": 1, \"amount\": \"14000\", \"invoice_date\": \"2026-10-26\", \"invoice_number\": \"INV-530\"}','2026-10-28 10:39:42');
/*!40000 ALTER TABLE `audit_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `background_jobs`
--

DROP TABLE IF EXISTS `background_jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `background_jobs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `job_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `params` json DEFAULT NULL,
  `result` text COLLATE utf8mb4_unicode_ci,
  `error` text COLLATE utf8mb4_unicode_ci,
  `attempts` int DEFAULT NULL,
  `max_attempts` int DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `started_at` datetime DEFAULT NULL,
  `finished_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=117 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `background_jobs`
--

LOCK TABLES `background_jobs` WRITE;
/*!40000 ALTER TABLE `background_jobs` DISABLE KEYS */;
INSERT INTO `background_jobs` VALUES (1,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:01:33','2026-10-28 09:01:33','2026-10-28 09:01:33'),(2,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:02:02','2026-10-28 09:02:02','2026-10-28 09:02:02'),(3,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:02:33','2026-10-28 09:02:33','2026-10-28 09:02:33'),(4,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:03:02','2026-10-28 09:03:03','2026-10-28 09:03:03'),(5,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:03:33','2026-10-28 09:03:33','2026-10-28 09:03:33'),(6,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:04:03','2026-10-28 09:04:03','2026-10-28 09:04:03'),(7,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:04:33','2026-10-28 09:04:33','2026-10-28 09:04:33'),(8,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:05:03','2026-10-28 09:05:03','2026-10-28 09:05:03'),(9,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:05:33','2026-10-28 09:05:33','2026-10-28 09:05:33'),(10,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:06:03','2026-10-28 09:06:03','2026-10-28 09:06:03'),(11,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:06:33','2026-10-28 09:06:33','2026-10-28 09:06:33'),(12,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:07:03','2026-10-28 09:07:03','2026-10-28 09:07:03'),(13,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:07:33','2026-10-28 09:07:33','2026-10-28 09:07:33'),(14,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:08:03','2026-10-28 09:08:03','2026-10-28 09:08:03'),(15,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:08:33','2026-10-28 09:08:33','2026-10-28 09:08:33'),(16,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:09:03','2026-10-28 09:09:03','2026-10-28 09:09:03'),(17,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:09:33','2026-10-28 09:09:33','2026-10-28 09:09:33'),(18,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:21:37','2026-10-28 09:21:37','2026-10-28 09:21:37'),(19,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:21:37','2026-10-28 09:21:37','2026-10-28 09:21:37'),(20,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:22:37','2026-10-28 09:22:37','2026-10-28 09:22:38'),(21,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:22:37','2026-10-28 09:22:37','2026-10-28 09:22:38'),(22,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:23:38','2026-10-28 09:23:38','2026-10-28 09:23:38'),(23,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:23:38','2026-10-28 09:23:38','2026-10-28 09:23:38'),(24,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:24:38','2026-10-28 09:24:38','2026-10-28 09:24:38'),(25,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:24:38','2026-10-28 09:24:38','2026-10-28 09:24:38'),(26,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:25:38','2026-10-28 09:25:38','2026-10-28 09:25:38'),(27,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:25:38','2026-10-28 09:25:38','2026-10-28 09:25:38'),(28,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:26:38','2026-10-28 09:26:38','2026-10-28 09:26:38'),(29,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:26:38','2026-10-28 09:26:38','2026-10-28 09:26:38'),(30,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:27:38','2026-10-28 09:27:38','2026-10-28 09:27:38'),(31,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:27:38','2026-10-28 09:27:38','2026-10-28 09:27:38'),(32,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:28:38','2026-10-28 09:28:38','2026-10-28 09:28:38'),(33,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:28:38','2026-10-28 09:28:38','2026-10-28 09:28:38'),(34,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:29:38','2026-10-28 09:29:38','2026-10-28 09:29:38'),(35,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:29:38','2026-10-28 09:29:38','2026-10-28 09:29:38'),(36,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:30:38','2026-10-28 09:30:38','2026-10-28 09:30:38'),(37,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:30:38','2026-10-28 09:30:38','2026-10-28 09:30:38'),(38,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:31:38','2026-10-28 09:31:38','2026-10-28 09:31:38'),(39,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:31:38','2026-10-28 09:31:38','2026-10-28 09:31:38'),(40,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:32:38','2026-10-28 09:32:38','2026-10-28 09:32:38'),(41,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:32:38','2026-10-28 09:32:38','2026-10-28 09:32:38'),(42,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:33:38','2026-10-28 09:33:38','2026-10-28 09:33:38'),(43,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:33:38','2026-10-28 09:33:38','2026-10-28 09:33:38'),(44,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:34:38','2026-10-28 09:34:38','2026-10-28 09:34:38'),(45,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:34:38','2026-10-28 09:34:38','2026-10-28 09:34:38'),(46,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:35:38','2026-10-28 09:35:38','2026-10-28 09:35:38'),(47,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:35:38','2026-10-28 09:35:38','2026-10-28 09:35:38'),(48,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:36:38','2026-10-28 09:36:38','2026-10-28 09:36:38'),(49,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:36:38','2026-10-28 09:36:38','2026-10-28 09:36:38'),(50,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:37:38','2026-10-28 09:37:38','2026-10-28 09:37:38'),(51,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:37:38','2026-10-28 09:37:38','2026-10-28 09:37:38'),(52,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:38:38','2026-10-28 09:38:38','2026-10-28 09:38:38'),(53,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:38:38','2026-10-28 09:38:38','2026-10-28 09:38:38'),(54,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:39:38','2026-10-28 09:39:38','2026-10-28 09:39:38'),(55,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:39:38','2026-10-28 09:39:38','2026-10-28 09:39:38'),(56,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:40:38','2026-10-28 09:40:38','2026-10-28 09:40:38'),(57,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:40:38','2026-10-28 09:40:38','2026-10-28 09:40:38'),(58,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:41:38','2026-10-28 09:41:38','2026-10-28 09:41:38'),(59,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:41:38','2026-10-28 09:41:38','2026-10-28 09:41:39'),(60,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:42:38','2026-10-28 09:42:39','2026-10-28 09:42:39'),(61,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:42:39','2026-10-28 09:42:39','2026-10-28 09:42:39'),(62,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:43:39','2026-10-28 09:43:39','2026-10-28 09:43:39'),(63,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:43:39','2026-10-28 09:43:39','2026-10-28 09:43:39'),(64,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:44:39','2026-10-28 09:44:39','2026-10-28 09:44:39'),(65,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:44:39','2026-10-28 09:44:39','2026-10-28 09:44:39'),(66,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:45:39','2026-10-28 09:45:39','2026-10-28 09:45:39'),(67,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:45:39','2026-10-28 09:45:39','2026-10-28 09:45:39'),(68,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:46:39','2026-10-28 09:46:39','2026-10-28 09:46:39'),(69,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:46:39','2026-10-28 09:46:39','2026-10-28 09:46:39'),(70,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:47:39','2026-10-28 09:47:39','2026-10-28 09:47:39'),(71,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:47:39','2026-10-28 09:47:39','2026-10-28 09:47:39'),(72,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:48:39','2026-10-28 09:48:39','2026-10-28 09:48:39'),(73,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:48:39','2026-10-28 09:48:39','2026-10-28 09:48:39'),(74,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:49:39','2026-10-28 09:49:39','2026-10-28 09:49:39'),(75,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:49:39','2026-10-28 09:49:39','2026-10-28 09:49:39'),(76,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:50:39','2026-10-28 09:50:39','2026-10-28 09:50:39'),(77,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:50:39','2026-10-28 09:50:39','2026-10-28 09:50:39'),(78,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:51:39','2026-10-28 09:51:39','2026-10-28 09:51:39'),(79,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:51:39','2026-10-28 09:51:39','2026-10-28 09:51:39'),(80,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:52:39','2026-10-28 09:52:39','2026-10-28 09:52:39'),(81,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:52:39','2026-10-28 09:52:39','2026-10-28 09:52:39'),(82,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:53:39','2026-10-28 09:53:39','2026-10-28 09:53:39'),(83,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 09:53:39','2026-10-28 09:53:39','2026-10-28 09:53:39'),(84,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:14:21','2026-10-28 10:14:21','2026-10-28 10:14:21'),(85,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:14:21','2026-10-28 10:14:21','2026-10-28 10:14:21'),(86,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:15:21','2026-10-28 10:15:21','2026-10-28 10:15:21'),(87,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:15:21','2026-10-28 10:15:21','2026-10-28 10:15:21'),(88,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:16:21','2026-10-28 10:16:21','2026-10-28 10:16:21'),(89,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:16:21','2026-10-28 10:16:21','2026-10-28 10:16:21'),(90,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:17:21','2026-10-28 10:17:21','2026-10-28 10:17:21'),(91,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:17:21','2026-10-28 10:17:21','2026-10-28 10:17:21'),(92,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:31:38','2026-10-28 10:31:38','2026-10-28 10:31:38'),(93,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:31:38','2026-10-28 10:31:38','2026-10-28 10:31:38'),(94,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:32:38','2026-10-28 10:32:38','2026-10-28 10:32:38'),(95,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:32:38','2026-10-28 10:32:38','2026-10-28 10:32:38'),(96,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:33:38','2026-10-28 10:33:38','2026-10-28 10:33:38'),(97,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:33:38','2026-10-28 10:33:38','2026-10-28 10:33:38'),(98,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:34:38','2026-10-28 10:34:38','2026-10-28 10:34:38'),(99,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:34:38','2026-10-28 10:34:38','2026-10-28 10:34:38'),(100,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:35:38','2026-10-28 10:35:38','2026-10-28 10:35:38'),(101,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:35:38','2026-10-28 10:35:38','2026-10-28 10:35:38'),(102,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:36:38','2026-10-28 10:36:38','2026-10-28 10:36:38'),(103,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:36:38','2026-10-28 10:36:38','2026-10-28 10:36:38'),(104,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:37:38','2026-10-28 10:37:38','2026-10-28 10:37:38'),(105,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:37:38','2026-10-28 10:37:38','2026-10-28 10:37:38'),(106,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:38:38','2026-10-28 10:38:38','2026-10-28 10:38:38'),(107,'process_outbox','success','{}','processed 6 messages',NULL,1,3,NULL,'2026-10-28 10:39:38','2026-10-28 10:39:38','2026-10-28 10:39:38'),(108,'report_export','success','{\"format\": \"xlsx\", \"report\": \"sales\", \"filters\": {}}','exports\\sales_report_108.xlsx',NULL,1,3,8,'2026-10-28 10:39:42','2026-10-28 10:39:42','2026-10-28 10:39:42'),(109,'daily_summary','success','{}','Orders today: 1. By status: {\'delivered\': 1}. Low stock rows: 0.',NULL,1,3,2,'2026-10-28 10:39:44','2026-10-28 10:39:44','2026-10-28 10:39:44'),(110,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:40:38','2026-10-28 10:40:38','2026-10-28 10:40:38'),(111,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:41:38','2026-10-28 10:41:38','2026-10-28 10:41:38'),(112,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:42:38','2026-10-28 10:42:38','2026-10-28 10:42:38'),(113,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:43:38','2026-10-28 10:43:38','2026-10-28 10:43:38'),(114,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:44:38','2026-10-28 10:44:38','2026-10-28 10:44:38'),(115,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:45:38','2026-10-28 10:45:38','2026-10-28 10:45:38'),(116,'process_outbox','success','{}','processed 0 messages',NULL,1,3,NULL,'2026-10-28 10:46:38','2026-10-28 10:46:38','2026-10-28 10:46:38');
/*!40000 ALTER TABLE `background_jobs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `brands`
--

DROP TABLE IF EXISTS `brands`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `brands` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `brands`
--

LOCK TABLES `brands` WRITE;
/*!40000 ALTER TABLE `brands` DISABLE KEYS */;
INSERT INTO `brands` VALUES (1,'Samsung',NULL,1,'2026-10-28 09:00:49'),(2,'boAt',NULL,1,'2026-10-28 09:00:49'),(3,'UrbanWear',NULL,1,'2026-10-28 09:00:49');
/*!40000 ALTER TABLE `brands` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart_items`
--

DROP TABLE IF EXISTS `cart_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cart_id` int NOT NULL,
  `product_id` int NOT NULL,
  `variant_id` int DEFAULT NULL,
  `quantity` int NOT NULL,
  `added_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cart_id` (`cart_id`),
  KEY `product_id` (`product_id`),
  KEY `variant_id` (`variant_id`),
  CONSTRAINT `cart_items_ibfk_1` FOREIGN KEY (`cart_id`) REFERENCES `carts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `cart_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `cart_items_ibfk_3` FOREIGN KEY (`variant_id`) REFERENCES `product_variants` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_items`
--

LOCK TABLES `cart_items` WRITE;
/*!40000 ALTER TABLE `cart_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `cart_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `carts`
--

DROP TABLE IF EXISTS `carts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `carts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `coupon_code` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `carts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carts`
--

LOCK TABLES `carts` WRITE;
/*!40000 ALTER TABLE `carts` DISABLE KEYS */;
INSERT INTO `carts` VALUES (1,9,NULL,'2026-10-28 10:39:36');
/*!40000 ALTER TABLE `carts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `parent_id` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `parent_id` (`parent_id`),
  CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Electronics','electronics',NULL,NULL,1,'2026-10-28 09:00:49'),(2,'Mobiles','mobiles',NULL,1,1,'2026-10-28 09:00:49'),(3,'Fashion','fashion',NULL,NULL,1,'2026-10-28 09:00:49'),(4,'T-Shirts','t-shirts',NULL,3,1,'2026-10-28 09:00:49'),(5,'Laptops 125','laptops-125',NULL,1,1,'2026-10-28 10:39:33');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cod_collections`
--

DROP TABLE IF EXISTS `cod_collections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cod_collections` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `expected_amount` decimal(12,2) NOT NULL,
  `collected_amount` decimal(12,2) DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `collected_by` int DEFAULT NULL,
  `collected_at` datetime DEFAULT NULL,
  `reconciled_by` int DEFAULT NULL,
  `reconciled_at` datetime DEFAULT NULL,
  `note` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_id` (`order_id`),
  CONSTRAINT `cod_collections_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cod_collections`
--

LOCK TABLES `cod_collections` WRITE;
/*!40000 ALTER TABLE `cod_collections` DISABLE KEYS */;
/*!40000 ALTER TABLE `cod_collections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cod_settings`
--

DROP TABLE IF EXISTS `cod_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cod_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `is_enabled` tinyint(1) DEFAULT NULL,
  `max_order_amount` decimal(12,2) DEFAULT NULL,
  `allowed_countries` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `blocked_postal_codes` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cod_settings`
--

LOCK TABLES `cod_settings` WRITE;
/*!40000 ALTER TABLE `cod_settings` DISABLE KEYS */;
INSERT INTO `cod_settings` VALUES (1,1,20000.00,'India','');
/*!40000 ALTER TABLE `cod_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `config_history`
--

DROP TABLE IF EXISTS `config_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `config_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `entity` varchar(60) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `entity_id` int DEFAULT NULL,
  `action` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `data` json DEFAULT NULL,
  `changed_by` int DEFAULT NULL,
  `changed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_config_history_entity` (`entity`),
  KEY `ix_config_history_entity_id` (`entity_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `config_history`
--

LOCK TABLES `config_history` WRITE;
/*!40000 ALTER TABLE `config_history` DISABLE KEYS */;
INSERT INTO `config_history` VALUES (1,'supplier',2,'registered','{\"kind\": \"supplier\", \"name\": \"Gadget Wholesale\", \"email\": \"gw444@test.com\", \"phone\": \"9000011111\", \"address\": null, \"gst_number\": null, \"contact_name\": null}',4,'2026-10-28 10:39:41'),(2,'supplier',2,'status:approved','{\"from\": \"pending\", \"note\": null}',2,'2026-10-28 10:39:41');
/*!40000 ALTER TABLE `config_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `coupons`
--

DROP TABLE IF EXISTS `coupons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `coupons` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `discount_type` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` decimal(10,2) NOT NULL,
  `max_discount` decimal(10,2) DEFAULT NULL,
  `min_purchase` decimal(10,2) DEFAULT NULL,
  `valid_from` datetime DEFAULT NULL,
  `valid_to` datetime DEFAULT NULL,
  `usage_limit` int DEFAULT NULL,
  `used_count` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `coupons`
--

LOCK TABLES `coupons` WRITE;
/*!40000 ALTER TABLE `coupons` DISABLE KEYS */;
INSERT INTO `coupons` VALUES (1,'WELCOME10','10% off up to 500','percent',10.00,500.00,499.00,'2026-10-27 09:00:49','2027-01-26 09:00:49',NULL,1,1,'2026-10-28 09:00:49'),(2,'FLAT100','Flat 100 off','fixed',100.00,NULL,999.00,NULL,NULL,100,0,1,'2026-10-28 09:00:49');
/*!40000 ALTER TABLE `coupons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `deactivation_requests`
--

DROP TABLE IF EXISTS `deactivation_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deactivation_requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `reason` text COLLATE utf8mb4_unicode_ci,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reviewed_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `reviewed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `deactivation_requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deactivation_requests`
--

LOCK TABLES `deactivation_requests` WRITE;
/*!40000 ALTER TABLE `deactivation_requests` DISABLE KEYS */;
/*!40000 ALTER TABLE `deactivation_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `delivery_assignments`
--

DROP TABLE IF EXISTS `delivery_assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `delivery_assignments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `shipment_id` int DEFAULT NULL,
  `assigned_to` int DEFAULT NULL,
  `provider_id` int DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `attempts` int DEFAULT NULL,
  `receiver_name` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `proof_note` text COLLATE utf8mb4_unicode_ci,
  `delivered_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `shipment_id` (`shipment_id`),
  KEY `assigned_to` (`assigned_to`),
  KEY `provider_id` (`provider_id`),
  CONSTRAINT `delivery_assignments_ibfk_1` FOREIGN KEY (`assigned_to`) REFERENCES `users` (`id`),
  CONSTRAINT `delivery_assignments_ibfk_2` FOREIGN KEY (`provider_id`) REFERENCES `shipping_providers` (`id`),
  CONSTRAINT `delivery_assignments_ibfk_3` FOREIGN KEY (`shipment_id`) REFERENCES `shipments` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delivery_assignments`
--

LOCK TABLES `delivery_assignments` WRITE;
/*!40000 ALTER TABLE `delivery_assignments` DISABLE KEYS */;
INSERT INTO `delivery_assignments` VALUES (1,1,7,NULL,'delivered',2,'Ravi',NULL,'2026-10-28 10:39:39','2026-10-28 10:39:39');
/*!40000 ALTER TABLE `delivery_assignments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `delivery_attempts`
--

DROP TABLE IF EXISTS `delivery_attempts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `delivery_attempts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `assignment_id` int DEFAULT NULL,
  `attempt_no` int DEFAULT NULL,
  `result` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reason` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `attempted_by` int DEFAULT NULL,
  `attempted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_delivery_attempts_assignment_id` (`assignment_id`),
  CONSTRAINT `delivery_attempts_ibfk_1` FOREIGN KEY (`assignment_id`) REFERENCES `delivery_assignments` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delivery_attempts`
--

LOCK TABLES `delivery_attempts` WRITE;
/*!40000 ALTER TABLE `delivery_attempts` DISABLE KEYS */;
INSERT INTO `delivery_attempts` VALUES (1,1,1,'failed','Customer not home',7,'2026-10-28 10:39:39'),(2,1,2,'delivered',NULL,7,'2026-10-28 10:39:39');
/*!40000 ALTER TABLE `delivery_attempts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exchange_events`
--

DROP TABLE IF EXISTS `exchange_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exchange_events` (
  `id` int NOT NULL AUTO_INCREMENT,
  `exchange_id` int DEFAULT NULL,
  `status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `note` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `changed_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_exchange_events_exchange_id` (`exchange_id`),
  CONSTRAINT `exchange_events_ibfk_1` FOREIGN KEY (`exchange_id`) REFERENCES `exchange_requests` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exchange_events`
--

LOCK TABLES `exchange_events` WRITE;
/*!40000 ALTER TABLE `exchange_events` DISABLE KEYS */;
/*!40000 ALTER TABLE `exchange_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exchange_requests`
--

DROP TABLE IF EXISTS `exchange_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exchange_requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `exchange_no` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `order_id` int NOT NULL,
  `order_item_id` int NOT NULL,
  `user_id` int NOT NULL,
  `replacement_variant_id` int DEFAULT NULL,
  `replacement_inventory_id` int DEFAULT NULL,
  `quantity` int NOT NULL,
  `reason` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `exchange_no` (`exchange_no`),
  KEY `order_id` (`order_id`),
  KEY `order_item_id` (`order_item_id`),
  KEY `replacement_inventory_id` (`replacement_inventory_id`),
  KEY `replacement_variant_id` (`replacement_variant_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `exchange_requests_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `exchange_requests_ibfk_2` FOREIGN KEY (`order_item_id`) REFERENCES `order_items` (`id`),
  CONSTRAINT `exchange_requests_ibfk_3` FOREIGN KEY (`replacement_inventory_id`) REFERENCES `inventory` (`id`),
  CONSTRAINT `exchange_requests_ibfk_4` FOREIGN KEY (`replacement_variant_id`) REFERENCES `product_variants` (`id`),
  CONSTRAINT `exchange_requests_ibfk_5` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exchange_requests`
--

LOCK TABLES `exchange_requests` WRITE;
/*!40000 ALTER TABLE `exchange_requests` DISABLE KEYS */;
/*!40000 ALTER TABLE `exchange_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory`
--

DROP TABLE IF EXISTS `inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventory` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `variant_id` int DEFAULT NULL,
  `warehouse_id` int NOT NULL,
  `quantity` int NOT NULL,
  `reserved` int NOT NULL,
  `min_threshold` int DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_stock_row` (`product_id`,`variant_id`,`warehouse_id`),
  KEY `variant_id` (`variant_id`),
  KEY `warehouse_id` (`warehouse_id`),
  CONSTRAINT `inventory_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `inventory_ibfk_2` FOREIGN KEY (`variant_id`) REFERENCES `product_variants` (`id`) ON DELETE CASCADE,
  CONSTRAINT `inventory_ibfk_3` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`),
  CONSTRAINT `ck_qty_positive` CHECK ((`quantity` >= 0)),
  CONSTRAINT `ck_reserved_positive` CHECK ((`reserved` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory`
--

LOCK TABLES `inventory` WRITE;
/*!40000 ALTER TABLE `inventory` DISABLE KEYS */;
INSERT INTO `inventory` VALUES (1,1,NULL,1,46,0,10,'2026-10-28 10:39:40'),(2,1,NULL,2,23,0,5,'2026-10-28 10:39:35'),(3,2,NULL,1,100,0,5,'2026-10-28 09:00:49'),(4,3,1,1,40,0,5,'2026-10-28 09:00:49'),(5,3,2,1,40,0,5,'2026-10-28 09:00:49'),(6,3,3,1,40,0,5,'2026-10-28 09:00:49'),(7,4,NULL,1,25,0,5,'2026-10-28 10:39:34');
/*!40000 ALTER TABLE `inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message_providers`
--

DROP TABLE IF EXISTS `message_providers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `message_providers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `channel` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `config` json DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message_providers`
--

LOCK TABLES `message_providers` WRITE;
/*!40000 ALTER TABLE `message_providers` DISABLE KEYS */;
/*!40000 ALTER TABLE `message_providers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `title` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `message` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `kind` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_notifications_user_id` (`user_id`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES (1,9,'Order ORD-261028-J09E4XCN placed','Thanks! Order total 30087.64. Please complete payment.','order',0,'2026-10-28 10:39:36'),(2,5,'New order','ORD-261028-J09E4XCN - 30087.64','order',0,'2026-10-28 10:39:36'),(3,9,'Order ORD-261028-J09E4XCN confirmed','Your order ORD-261028-J09E4XCN is now confirmed.','order',0,'2026-10-28 10:39:37'),(4,9,'Payment successful','We received 30087.64 INR for order ORD-261028-J09E4XCN.','payment',0,'2026-10-28 10:39:37'),(5,9,'Refund update','Refund RF-261028-AJ291DS7 of 100.00 for order ORD-261028-J09E4XCN is succeeded.','refund',0,'2026-10-28 10:39:38'),(6,9,'Order ORD-261028-J09E4XCN processing','Your order ORD-261028-J09E4XCN is now processing.','order',0,'2026-10-28 10:39:38'),(7,9,'Order ORD-261028-J09E4XCN shipped','Your order ORD-261028-J09E4XCN is now shipped.','order',0,'2026-10-28 10:39:38'),(8,9,'Order ORD-261028-J09E4XCN delivered','Your order ORD-261028-J09E4XCN is now delivered.','order',0,'2026-10-28 10:39:39'),(9,9,'Return RET-261028-P8SE3ZTY approved','Your return request was approved.','order',0,'2026-10-28 10:39:40'),(10,9,'Refund update','Refund RF-261028-Z8ZKNYCE of 15043.82 for order ORD-261028-J09E4XCN is succeeded.','refund',0,'2026-10-28 10:39:40'),(11,9,'Ticket TKT-261028-597YMAX9 opened','Our support team will get back to you soon.','general',0,'2026-10-28 10:39:40'),(12,9,'New reply on TKT-261028-597YMAX9','Checking now','general',0,'2026-10-28 10:39:40'),(13,9,'Ticket TKT-261028-597YMAX9 resolved','Delivered today','general',0,'2026-10-28 10:39:40'),(14,1,'Daily summary','Orders today: 1. By status: {\'delivered\': 1}. Low stock rows: 0.','general',0,'2026-10-28 10:39:44'),(15,2,'Daily summary','Orders today: 1. By status: {\'delivered\': 1}. Low stock rows: 0.','general',0,'2026-10-28 10:39:44'),(16,4,'Daily summary','Orders today: 1. By status: {\'delivered\': 1}. Low stock rows: 0.','general',0,'2026-10-28 10:39:44');
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_cancellations`
--

DROP TABLE IF EXISTS `order_cancellations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_cancellations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int DEFAULT NULL,
  `requested_by` int DEFAULT NULL,
  `reason` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `outcome` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `refund_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_id` (`order_id`),
  CONSTRAINT `order_cancellations_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_cancellations`
--

LOCK TABLES `order_cancellations` WRITE;
/*!40000 ALTER TABLE `order_cancellations` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_cancellations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `product_id` int NOT NULL,
  `variant_id` int DEFAULT NULL,
  `inventory_id` int DEFAULT NULL,
  `sku` varchar(60) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `product_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `product_description` text COLLATE utf8mb4_unicode_ci,
  `variant_label` varchar(80) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `unit_price` decimal(12,2) NOT NULL,
  `quantity` int NOT NULL,
  `discount` decimal(12,2) DEFAULT NULL,
  `tax` decimal(12,2) DEFAULT NULL,
  `line_total` decimal(12,2) NOT NULL,
  `fulfillment_status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inventory_id` (`inventory_id`),
  KEY `order_id` (`order_id`),
  KEY `product_id` (`product_id`),
  KEY `variant_id` (`variant_id`),
  CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`inventory_id`) REFERENCES `inventory` (`id`),
  CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `order_items_ibfk_3` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `order_items_ibfk_4` FOREIGN KEY (`variant_id`) REFERENCES `product_variants` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES (1,1,1,NULL,1,'SAM-M14','Samsung Galaxy M14','6000mAh battery, 50MP camera',NULL,12999.00,2,500.00,4589.64,30087.64,'delivered');
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_status_history`
--

DROP TABLE IF EXISTS `order_status_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_status_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int DEFAULT NULL,
  `from_status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `to_status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `changed_by` int DEFAULT NULL,
  `note` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_order_status_history_order_id` (`order_id`),
  CONSTRAINT `order_status_history_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_status_history`
--

LOCK TABLES `order_status_history` WRITE;
/*!40000 ALTER TABLE `order_status_history` DISABLE KEYS */;
INSERT INTO `order_status_history` VALUES (1,1,NULL,'pending',9,'Order placed','2026-10-28 10:39:36'),(2,1,'pending','confirmed',NULL,'Payment received','2026-10-28 10:39:37'),(3,1,'confirmed','processing',5,'Packing started','2026-10-28 10:39:38'),(4,1,'processing','shipped',5,'Dispatched via shipment SHP-261028-XK4HH580','2026-10-28 10:39:38'),(5,1,'shipped','delivered',7,'Delivered (SHP-261028-XK4HH580)','2026-10-28 10:39:39');
/*!40000 ALTER TABLE `order_status_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_number` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` int NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `payment_method` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `payment_status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `shipping_address_id` int DEFAULT NULL,
  `billing_address_id` int DEFAULT NULL,
  `shipping_address_text` text COLLATE utf8mb4_unicode_ci,
  `billing_address_text` text COLLATE utf8mb4_unicode_ci,
  `shipping_method_id` int DEFAULT NULL,
  `coupon_code` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `subtotal` decimal(12,2) DEFAULT NULL,
  `discount_total` decimal(12,2) DEFAULT NULL,
  `tax_total` decimal(12,2) DEFAULT NULL,
  `shipping_total` decimal(12,2) DEFAULT NULL,
  `grand_total` decimal(12,2) DEFAULT NULL,
  `tax_breakdown` json DEFAULT NULL,
  `idempotency_key` varchar(80) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notes` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_number` (`order_number`),
  UNIQUE KEY `idempotency_key` (`idempotency_key`),
  KEY `billing_address_id` (`billing_address_id`),
  KEY `shipping_address_id` (`shipping_address_id`),
  KEY `shipping_method_id` (`shipping_method_id`),
  KEY `ix_orders_created_at` (`created_at`),
  KEY `ix_orders_status` (`status`),
  KEY `ix_orders_user_id` (`user_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`billing_address_id`) REFERENCES `addresses` (`id`),
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`shipping_address_id`) REFERENCES `addresses` (`id`),
  CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`shipping_method_id`) REFERENCES `shipping_methods` (`id`),
  CONSTRAINT `orders_ibfk_4` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,'ORD-261028-J09E4XCN',9,'delivered','card','partially_refunded',1,1,'Ravi Customer, Plot 12, Road No 3, Banjara Hills, Hyderabad, Telangana, 500034, India, 9876543210','Ravi Customer, Plot 12, Road No 3, Banjara Hills, Hyderabad, Telangana, 500034, India, 9876543210',1,'WELCOME10',25998.00,500.00,4589.64,0.00,30087.64,'{\"GST 18% Mobiles (18.00%)\": \"4589.64\"}','9:pm-696',NULL,'2026-10-28 10:39:36','2026-10-28 10:39:39');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `outbound_messages`
--

DROP TABLE IF EXISTS `outbound_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `outbound_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `channel` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `recipient` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `subject` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `body` text COLLATE utf8mb4_unicode_ci,
  `template` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `attempts` int DEFAULT NULL,
  `max_attempts` int DEFAULT NULL,
  `last_error` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `sent_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `outbound_messages`
--

LOCK TABLES `outbound_messages` WRITE;
/*!40000 ALTER TABLE `outbound_messages` DISABLE KEYS */;
INSERT INTO `outbound_messages` VALUES (1,'email','postman397@test.com','Verify your ShopSphere account','Hi Postman User, verify your email here: /auth/verify-email?token=ZhiHE9WxUkPk81Q-dEtJCYj9lqlWYv-n','verification','sent',1,3,NULL,'2026-10-28 10:39:29','2026-10-28 10:39:38'),(2,'email','customer@shopsphere.com','Order ORD-261028-J09E4XCN placed','Thanks! Order total 30087.64. Please complete payment.','order','sent',1,3,NULL,'2026-10-28 10:39:36','2026-10-28 10:39:38'),(3,'sms','9876543210',NULL,'Order ORD-261028-J09E4XCN placed: Thanks! Order total 30087.64. Please complete payment.','order','sent',1,3,NULL,'2026-10-28 10:39:36','2026-10-28 10:39:38'),(4,'email','customer@shopsphere.com','Order ORD-261028-J09E4XCN confirmed','Your order ORD-261028-J09E4XCN is now confirmed.','order','sent',1,3,NULL,'2026-10-28 10:39:37','2026-10-28 10:39:38'),(5,'email','customer@shopsphere.com','Payment successful','We received 30087.64 INR for order ORD-261028-J09E4XCN.','payment','sent',1,3,NULL,'2026-10-28 10:39:37','2026-10-28 10:39:38'),(6,'email','customer@shopsphere.com','Refund update','Refund RF-261028-AJ291DS7 of 100.00 for order ORD-261028-J09E4XCN is succeeded.','refund','sent',1,3,NULL,'2026-10-28 10:39:38','2026-10-28 10:39:38'),(7,'email','customer@shopsphere.com','Order ORD-261028-J09E4XCN processing','Your order ORD-261028-J09E4XCN is now processing.','order','sent',1,3,NULL,'2026-10-28 10:39:38','2026-10-28 10:39:41'),(8,'email','customer@shopsphere.com','Order ORD-261028-J09E4XCN shipped','Your order ORD-261028-J09E4XCN is now shipped.','order','sent',1,3,NULL,'2026-10-28 10:39:38','2026-10-28 10:39:41'),(9,'email','customer@shopsphere.com','Order ORD-261028-J09E4XCN delivered','Your order ORD-261028-J09E4XCN is now delivered.','order','sent',1,3,NULL,'2026-10-28 10:39:39','2026-10-28 10:39:41'),(10,'email','customer@shopsphere.com','Return RET-261028-P8SE3ZTY approved','Your return request was approved.','order','sent',1,3,NULL,'2026-10-28 10:39:40','2026-10-28 10:39:41'),(11,'email','customer@shopsphere.com','Refund update','Refund RF-261028-Z8ZKNYCE of 15043.82 for order ORD-261028-J09E4XCN is succeeded.','refund','sent',1,3,NULL,'2026-10-28 10:39:40','2026-10-28 10:39:41'),(12,'email','customer@shopsphere.com','Ticket TKT-261028-597YMAX9 opened','Our support team will get back to you soon.','general','sent',1,3,NULL,'2026-10-28 10:39:40','2026-10-28 10:39:41'),(13,'email','customer@shopsphere.com','New reply on TKT-261028-597YMAX9','Checking now','general','sent',1,3,NULL,'2026-10-28 10:39:40','2026-10-28 10:39:41'),(14,'email','customer@shopsphere.com','Ticket TKT-261028-597YMAX9 resolved','Delivered today','general','sent',1,3,NULL,'2026-10-28 10:39:40','2026-10-28 10:39:41');
/*!40000 ALTER TABLE `outbound_messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment_events`
--

DROP TABLE IF EXISTS `payment_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_events` (
  `id` int NOT NULL AUTO_INCREMENT,
  `payment_id` int DEFAULT NULL,
  `event_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `gateway_event_id` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `payload` json DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gateway_event_id` (`gateway_event_id`),
  KEY `ix_payment_events_payment_id` (`payment_id`),
  CONSTRAINT `payment_events_ibfk_1` FOREIGN KEY (`payment_id`) REFERENCES `payments` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_events`
--

LOCK TABLES `payment_events` WRITE;
/*!40000 ALTER TABLE `payment_events` DISABLE KEYS */;
INSERT INTO `payment_events` VALUES (1,1,'intent.created','pending',NULL,'{\"ref\": \"sb_pi_0bb6cc64ba474ba595da\"}','2026-10-28 10:39:37'),(2,1,'payment.succeeded','succeeded','evt_1fafda02fd5d41ef8b0e','{\"id\": \"evt_1fafda02fd5d41ef8b0e\", \"data\": {\"ref\": \"sb_pi_0bb6cc64ba474ba595da\", \"reason\": null}, \"type\": \"payment.succeeded\"}','2026-10-28 10:39:37');
/*!40000 ALTER TABLE `payment_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `user_id` int NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `currency` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `method` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `gateway` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `gateway_ref` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `client_secret` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `idempotency_key` varchar(80) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `failure_reason` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gateway_ref` (`gateway_ref`),
  UNIQUE KEY `idempotency_key` (`idempotency_key`),
  KEY `user_id` (`user_id`),
  KEY `ix_payments_order_id` (`order_id`),
  KEY `ix_payments_status` (`status`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
INSERT INTO `payments` VALUES (1,1,9,30087.64,'INR','card','sandbox','sb_pi_0bb6cc64ba474ba595da','sb_pi_0bb6cc64ba474ba595da_secret_eca8c9a4bc','succeeded','pay:9:1',NULL,'2026-10-28 10:39:37','2026-10-28 10:39:37');
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissions`
--

LOCK TABLES `permissions` WRITE;
/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
INSERT INTO `permissions` VALUES (1,'*',NULL),(2,'users.manage',NULL),(3,'products.manage',NULL),(4,'orders.manage',NULL),(5,'reports.view',NULL),(6,'audit.view',NULL),(7,'pricing.manage',NULL),(8,'categories.manage',NULL),(9,'inventory.manage',NULL),(10,'warehouses.manage',NULL),(11,'purchase_orders.manage',NULL),(12,'returns.manage',NULL),(13,'shipments.manage',NULL),(14,'tickets.manage',NULL),(15,'reviews.moderate',NULL),(16,'shop',NULL),(17,'deliveries.manage',NULL),(18,'payments.view',NULL),(19,'refunds.manage',NULL),(20,'invoices.manage',NULL);
/*!40000 ALTER TABLE `permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `price_history`
--

DROP TABLE IF EXISTS `price_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `price_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int DEFAULT NULL,
  `variant_id` int DEFAULT NULL,
  `old_base` decimal(12,2) DEFAULT NULL,
  `new_base` decimal(12,2) DEFAULT NULL,
  `old_sale` decimal(12,2) DEFAULT NULL,
  `new_sale` decimal(12,2) DEFAULT NULL,
  `changed_by` int DEFAULT NULL,
  `changed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_price_history_product_id` (`product_id`),
  CONSTRAINT `price_history_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `price_history`
--

LOCK TABLES `price_history` WRITE;
/*!40000 ALTER TABLE `price_history` DISABLE KEYS */;
INSERT INTO `price_history` VALUES (1,4,NULL,NULL,55000.00,NULL,NULL,3,'2026-10-28 10:39:34'),(2,4,NULL,55000.00,54000.00,NULL,49999.00,3,'2026-10-28 10:39:34');
/*!40000 ALTER TABLE `price_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_answers`
--

DROP TABLE IF EXISTS `product_answers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_answers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `question_id` int NOT NULL,
  `user_id` int NOT NULL,
  `text` varchar(2000) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `question_id` (`question_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `product_answers_ibfk_1` FOREIGN KEY (`question_id`) REFERENCES `product_questions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `product_answers_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_answers`
--

LOCK TABLES `product_answers` WRITE;
/*!40000 ALTER TABLE `product_answers` DISABLE KEYS */;
INSERT INTO `product_answers` VALUES (1,1,6,'Yes, it supports 5G bands.','visible','2026-10-28 10:39:40');
/*!40000 ALTER TABLE `product_answers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_attribute_values`
--

DROP TABLE IF EXISTS `product_attribute_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_attribute_values` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `attribute_id` int NOT NULL,
  `value` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_product_attribute` (`product_id`,`attribute_id`),
  KEY `attribute_id` (`attribute_id`),
  CONSTRAINT `product_attribute_values_ibfk_1` FOREIGN KEY (`attribute_id`) REFERENCES `attributes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `product_attribute_values_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_attribute_values`
--

LOCK TABLES `product_attribute_values` WRITE;
/*!40000 ALTER TABLE `product_attribute_values` DISABLE KEYS */;
INSERT INTO `product_attribute_values` VALUES (1,1,2,'6'),(2,1,1,'Blue'),(3,4,1,'Black');
/*!40000 ALTER TABLE `product_attribute_values` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_files`
--

DROP TABLE IF EXISTS `product_files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_files` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `variant_id` int DEFAULT NULL,
  `file_kind` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `original_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `stored_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `size_bytes` int DEFAULT NULL,
  `uploaded_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`),
  KEY `variant_id` (`variant_id`),
  CONSTRAINT `product_files_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `product_files_ibfk_2` FOREIGN KEY (`variant_id`) REFERENCES `product_variants` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_files`
--

LOCK TABLES `product_files` WRITE;
/*!40000 ALTER TABLE `product_files` DISABLE KEYS */;
/*!40000 ALTER TABLE `product_files` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_questions`
--

DROP TABLE IF EXISTS `product_questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_questions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `user_id` int NOT NULL,
  `text` varchar(1000) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_product_questions_product_id` (`product_id`),
  CONSTRAINT `product_questions_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `product_questions_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_questions`
--

LOCK TABLES `product_questions` WRITE;
/*!40000 ALTER TABLE `product_questions` DISABLE KEYS */;
INSERT INTO `product_questions` VALUES (1,1,10,'Does it support 5G?','answered','2026-10-28 10:39:40');
/*!40000 ALTER TABLE `product_questions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_variants`
--

DROP TABLE IF EXISTS `product_variants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_variants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `sku` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `size` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `color` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `price` decimal(12,2) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sku` (`sku`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `product_variants_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_variants`
--

LOCK TABLES `product_variants` WRITE;
/*!40000 ALTER TABLE `product_variants` DISABLE KEYS */;
INSERT INTO `product_variants` VALUES (1,3,'UW-TEE-BLA-M','M','Black',NULL,1,'2026-10-28 09:00:49'),(2,3,'UW-TEE-BLA-L','L','Black',NULL,1,'2026-10-28 09:00:49'),(3,3,'UW-TEE-WHI-M','M','White',NULL,1,'2026-10-28 09:00:49'),(4,4,'DELL-V-617','15 inch','Silver',56000.00,1,'2026-10-28 10:39:34');
/*!40000 ALTER TABLE `product_variants` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sku` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `category_id` int NOT NULL,
  `brand_id` int DEFAULT NULL,
  `seller_id` int DEFAULT NULL,
  `base_price` decimal(12,2) NOT NULL,
  `sale_price` decimal(12,2) DEFAULT NULL,
  `sale_start` datetime DEFAULT NULL,
  `sale_end` datetime DEFAULT NULL,
  `cod_allowed` tinyint(1) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sku` (`sku`),
  KEY `brand_id` (`brand_id`),
  KEY `category_id` (`category_id`),
  KEY `seller_id` (`seller_id`),
  KEY `ix_products_name` (`name`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`brand_id`) REFERENCES `brands` (`id`),
  CONSTRAINT `products_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`),
  CONSTRAINT `products_ibfk_3` FOREIGN KEY (`seller_id`) REFERENCES `suppliers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,'Samsung Galaxy M14','SAM-M14','6000mAh battery, 50MP camera',2,1,NULL,14999.00,12999.00,NULL,NULL,1,1,'2026-10-28 09:00:49','2026-10-28 09:00:49'),(2,'boAt Airdopes 141','BOAT-AIR141','42h playback, ENx tech',1,2,NULL,1499.00,NULL,NULL,NULL,1,1,'2026-10-28 09:00:49','2026-10-28 09:00:49'),(3,'Basic Cotton T-Shirt','UW-TEE-BASIC','100% cotton regular fit',4,3,NULL,599.00,NULL,NULL,NULL,1,1,'2026-10-28 09:00:49','2026-10-28 09:00:49'),(4,'Dell Inspiron 15','DELL-INS-809','i5, 16GB',1,1,NULL,54000.00,49999.00,NULL,NULL,1,1,'2026-10-28 10:39:34','2026-10-28 10:39:34');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profile_history`
--

DROP TABLE IF EXISTS `profile_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `profile_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `field` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `old_value` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `new_value` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `changed_by` int DEFAULT NULL,
  `changed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_profile_history_user_id` (`user_id`),
  CONSTRAINT `profile_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profile_history`
--

LOCK TABLES `profile_history` WRITE;
/*!40000 ALTER TABLE `profile_history` DISABLE KEYS */;
INSERT INTO `profile_history` VALUES (1,9,'full_name','Ravi Customer','Ravi Kumar',9,'2026-10-28 10:39:32');
/*!40000 ALTER TABLE `profile_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `promotions`
--

DROP TABLE IF EXISTS `promotions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `promotions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `scope` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `product_id` int DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  `discount_type` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` decimal(10,2) NOT NULL,
  `min_quantity` int DEFAULT NULL,
  `start_at` datetime NOT NULL,
  `end_at` datetime NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `promotions_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE,
  CONSTRAINT `promotions_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `promotions`
--

LOCK TABLES `promotions` WRITE;
/*!40000 ALTER TABLE `promotions` DISABLE KEYS */;
INSERT INTO `promotions` VALUES (1,'T-Shirt Fest','category',NULL,4,'percent',10.00,2,'2026-10-27 09:00:49','2026-11-27 09:00:49',1,'2026-10-28 09:00:49');
/*!40000 ALTER TABLE `promotions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase_order_items`
--

DROP TABLE IF EXISTS `purchase_order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_order_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `po_id` int DEFAULT NULL,
  `product_id` int NOT NULL,
  `variant_id` int DEFAULT NULL,
  `quantity` int NOT NULL,
  `received_qty` int DEFAULT NULL,
  `unit_cost` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `po_id` (`po_id`),
  KEY `product_id` (`product_id`),
  KEY `variant_id` (`variant_id`),
  CONSTRAINT `purchase_order_items_ibfk_1` FOREIGN KEY (`po_id`) REFERENCES `purchase_orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `purchase_order_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `purchase_order_items_ibfk_3` FOREIGN KEY (`variant_id`) REFERENCES `product_variants` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_order_items`
--

LOCK TABLES `purchase_order_items` WRITE;
/*!40000 ALTER TABLE `purchase_order_items` DISABLE KEYS */;
INSERT INTO `purchase_order_items` VALUES (1,1,2,NULL,20,0,700.00);
/*!40000 ALTER TABLE `purchase_order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase_orders`
--

DROP TABLE IF EXISTS `purchase_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `po_number` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `supplier_id` int NOT NULL,
  `warehouse_id` int NOT NULL,
  `status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `expected_date` date DEFAULT NULL,
  `total_amount` decimal(12,2) DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `po_number` (`po_number`),
  KEY `supplier_id` (`supplier_id`),
  KEY `warehouse_id` (`warehouse_id`),
  CONSTRAINT `purchase_orders_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`),
  CONSTRAINT `purchase_orders_ibfk_2` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_orders`
--

LOCK TABLES `purchase_orders` WRITE;
/*!40000 ALTER TABLE `purchase_orders` DISABLE KEYS */;
INSERT INTO `purchase_orders` VALUES (1,'PO-261028-LIFFK0JZ',2,1,'sent',NULL,14000.00,4,'2026-10-28 10:39:41');
/*!40000 ALTER TABLE `purchase_orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `refresh_tokens`
--

DROP TABLE IF EXISTS `refresh_tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `refresh_tokens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `jti` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `expires_at` datetime NOT NULL,
  `revoked` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `jti` (`jti`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `refresh_tokens_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `refresh_tokens`
--

LOCK TABLES `refresh_tokens` WRITE;
/*!40000 ALTER TABLE `refresh_tokens` DISABLE KEYS */;
INSERT INTO `refresh_tokens` VALUES (1,9,'feff8394a3f74d68ad8b4d0c6bec377a','2026-11-04 10:39:22',0,'2026-10-28 10:39:22'),(2,10,'298168038b6c4aa79b4f91d1a238c46b','2026-11-04 10:39:23',0,'2026-10-28 10:39:23'),(3,2,'d0268dd31b274d009fabef141f107542','2026-11-04 10:39:24',0,'2026-10-28 10:39:24'),(4,3,'00d7e4e2296e494ca794c973ed453787','2026-11-04 10:39:25',0,'2026-10-28 10:39:25'),(5,4,'f4383ce3ec234858b8012e1a9f6fb9e5','2026-11-04 10:39:26',0,'2026-10-28 10:39:26'),(6,5,'9e646b8997344d17896da0ce8bac40d6','2026-11-04 10:39:26',0,'2026-10-28 10:39:26'),(7,6,'60bf2c77b6144d94aeb7025a96002878','2026-11-04 10:39:27',0,'2026-10-28 10:39:27'),(8,7,'3dffbd6fa7a94395aa5f60d0a4a3c26a','2026-11-04 10:39:28',0,'2026-10-28 10:39:28'),(9,8,'00d20dbb0bf0429e980e54b35686635b','2026-11-04 10:39:29',1,'2026-10-28 10:39:29'),(10,8,'85c3f9d0cad84fe4ba348850f701e5c8','2026-11-04 10:39:30',0,'2026-10-28 10:39:30');
/*!40000 ALTER TABLE `refresh_tokens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `refunds`
--

DROP TABLE IF EXISTS `refunds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `refunds` (
  `id` int NOT NULL AUTO_INCREMENT,
  `refund_no` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `payment_id` int DEFAULT NULL,
  `order_id` int NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `reason` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `gateway_ref` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `requested_by` int DEFAULT NULL,
  `processed_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `processed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `refund_no` (`refund_no`),
  KEY `payment_id` (`payment_id`),
  KEY `ix_refunds_order_id` (`order_id`),
  CONSTRAINT `refunds_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `refunds_ibfk_2` FOREIGN KEY (`payment_id`) REFERENCES `payments` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `refunds`
--

LOCK TABLES `refunds` WRITE;
/*!40000 ALTER TABLE `refunds` DISABLE KEYS */;
INSERT INTO `refunds` VALUES (1,'RF-261028-AJ291DS7',1,1,100.00,'Goodwill','succeeded','sb_re_6b604ccf5e8742ae94b7',8,8,'2026-10-28 10:39:38','2026-10-28 10:39:38'),(2,'RF-261028-Z8ZKNYCE',1,1,15043.82,'Return RET-261028-P8SE3ZTY','succeeded','sb_re_76078db0234c4a04b9cd',5,5,'2026-10-28 10:39:40','2026-10-28 10:39:40');
/*!40000 ALTER TABLE `refunds` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restock_alerts`
--

DROP TABLE IF EXISTS `restock_alerts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restock_alerts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inventory_id` int DEFAULT NULL,
  `available_qty` int DEFAULT NULL,
  `threshold` int DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `resolved_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_restock_alerts_inventory_id` (`inventory_id`),
  CONSTRAINT `restock_alerts_ibfk_1` FOREIGN KEY (`inventory_id`) REFERENCES `inventory` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restock_alerts`
--

LOCK TABLES `restock_alerts` WRITE;
/*!40000 ALTER TABLE `restock_alerts` DISABLE KEYS */;
/*!40000 ALTER TABLE `restock_alerts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `return_items`
--

DROP TABLE IF EXISTS `return_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `return_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `return_id` int DEFAULT NULL,
  `order_item_id` int DEFAULT NULL,
  `quantity` int NOT NULL,
  `reason` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `order_item_id` (`order_item_id`),
  KEY `return_id` (`return_id`),
  CONSTRAINT `return_items_ibfk_1` FOREIGN KEY (`order_item_id`) REFERENCES `order_items` (`id`),
  CONSTRAINT `return_items_ibfk_2` FOREIGN KEY (`return_id`) REFERENCES `return_requests` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `return_items`
--

LOCK TABLES `return_items` WRITE;
/*!40000 ALTER TABLE `return_items` DISABLE KEYS */;
INSERT INTO `return_items` VALUES (1,1,1,1,NULL);
/*!40000 ALTER TABLE `return_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `return_requests`
--

DROP TABLE IF EXISTS `return_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `return_requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `return_no` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `order_id` int NOT NULL,
  `user_id` int NOT NULL,
  `reason` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `admin_note` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `refund_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `return_no` (`return_no`),
  KEY `user_id` (`user_id`),
  KEY `ix_return_requests_order_id` (`order_id`),
  CONSTRAINT `return_requests_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `return_requests_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `return_requests`
--

LOCK TABLES `return_requests` WRITE;
/*!40000 ALTER TABLE `return_requests` DISABLE KEYS */;
INSERT INTO `return_requests` VALUES (1,'RET-261028-P8SE3ZTY',1,9,'Not needed','refunded',NULL,2,'2026-10-28 10:39:39','2026-10-28 10:39:40');
/*!40000 ALTER TABLE `return_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reviews`
--

DROP TABLE IF EXISTS `reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reviews` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `user_id` int NOT NULL,
  `order_id` int DEFAULT NULL,
  `rating` int NOT NULL,
  `title` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `comment` text COLLATE utf8mb4_unicode_ci,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `moderated_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_one_review` (`product_id`,`user_id`),
  KEY `order_id` (`order_id`),
  KEY `user_id` (`user_id`),
  KEY `ix_reviews_product_id` (`product_id`),
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `reviews_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reviews`
--

LOCK TABLES `reviews` WRITE;
/*!40000 ALTER TABLE `reviews` DISABLE KEYS */;
INSERT INTO `reviews` VALUES (1,1,9,1,5,'Love it','Battery is great','published',NULL,'2026-10-28 10:39:39');
/*!40000 ALTER TABLE `reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `revoked_tokens`
--

DROP TABLE IF EXISTS `revoked_tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `revoked_tokens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `jti` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `expires_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `jti` (`jti`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `revoked_tokens`
--

LOCK TABLES `revoked_tokens` WRITE;
/*!40000 ALTER TABLE `revoked_tokens` DISABLE KEYS */;
/*!40000 ALTER TABLE `revoked_tokens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role_permissions`
--

DROP TABLE IF EXISTS `role_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_permissions` (
  `role_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`role_id`,`permission_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_permissions`
--

LOCK TABLES `role_permissions` WRITE;
/*!40000 ALTER TABLE `role_permissions` DISABLE KEYS */;
INSERT INTO `role_permissions` VALUES (1,1),(2,2),(2,3),(3,3),(2,4),(5,4),(2,5),(9,5),(2,6),(3,7),(3,8),(4,9),(4,10),(4,11),(5,12),(5,13),(8,13),(6,14),(6,15),(7,16),(8,17),(9,18),(9,19),(9,20);
/*!40000 ALTER TABLE `role_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'super_admin','Super Admin'),(2,'admin','Admin'),(3,'product_manager','Product Manager'),(4,'inventory_manager','Inventory Manager'),(5,'order_manager','Order Manager'),(6,'support_agent','Support Agent'),(7,'customer','Customer'),(8,'delivery_manager','Delivery Manager'),(9,'finance_manager','Finance Manager');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shipments`
--

DROP TABLE IF EXISTS `shipments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shipments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `shipment_ref` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `order_id` int NOT NULL,
  `provider_id` int DEFAULT NULL,
  `tracking_number` varchar(80) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `weight_kg` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dispatched_at` datetime DEFAULT NULL,
  `delivered_at` datetime DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `shipment_ref` (`shipment_ref`),
  UNIQUE KEY `tracking_number` (`tracking_number`),
  KEY `provider_id` (`provider_id`),
  KEY `ix_shipments_order_id` (`order_id`),
  CONSTRAINT `shipments_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `shipments_ibfk_2` FOREIGN KEY (`provider_id`) REFERENCES `shipping_providers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shipments`
--

LOCK TABLES `shipments` WRITE;
/*!40000 ALTER TABLE `shipments` DISABLE KEYS */;
INSERT INTO `shipments` VALUES (1,'SHP-261028-XK4HH580',1,1,'DELHIVERYT2610285UR9M6','delivered',NULL,'2026-10-28 10:39:38','2026-10-28 10:39:39',5,'2026-10-28 10:39:38');
/*!40000 ALTER TABLE `shipments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shipping_methods`
--

DROP TABLE IF EXISTS `shipping_methods`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shipping_methods` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `base_charge` decimal(10,2) DEFAULT NULL,
  `per_item_charge` decimal(10,2) DEFAULT NULL,
  `free_above` decimal(10,2) DEFAULT NULL,
  `min_days` int DEFAULT NULL,
  `max_days` int DEFAULT NULL,
  `allowed_countries` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `max_items` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shipping_methods`
--

LOCK TABLES `shipping_methods` WRITE;
/*!40000 ALTER TABLE `shipping_methods` DISABLE KEYS */;
INSERT INTO `shipping_methods` VALUES (1,'Standard Delivery','STANDARD',49.00,0.00,999.00,3,6,'India',NULL,1),(2,'Express Delivery','EXPRESS',149.00,20.00,NULL,1,2,'India',10,1);
/*!40000 ALTER TABLE `shipping_methods` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shipping_providers`
--

DROP TABLE IF EXISTS `shipping_providers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shipping_providers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tracking_url` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shipping_providers`
--

LOCK TABLES `shipping_providers` WRITE;
/*!40000 ALTER TABLE `shipping_providers` DISABLE KEYS */;
INSERT INTO `shipping_providers` VALUES (1,'Delhivery','DELHIVERY','https://www.delhivery.com/track/package/{tracking}',1),(2,'Blue Dart','BLUEDART',NULL,1);
/*!40000 ALTER TABLE `shipping_providers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stock_movements`
--

DROP TABLE IF EXISTS `stock_movements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stock_movements` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inventory_id` int DEFAULT NULL,
  `change` int NOT NULL,
  `movement_type` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reference` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `note` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_stock_movements_inventory_id` (`inventory_id`),
  CONSTRAINT `stock_movements_ibfk_1` FOREIGN KEY (`inventory_id`) REFERENCES `inventory` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock_movements`
--

LOCK TABLES `stock_movements` WRITE;
/*!40000 ALTER TABLE `stock_movements` DISABLE KEYS */;
INSERT INTO `stock_movements` VALUES (1,7,25,'add','manual',NULL,4,'2026-10-28 10:39:34'),(2,1,-3,'transfer_out','TR-261028-QWKJVF23',NULL,4,'2026-10-28 10:39:35'),(3,2,3,'transfer_in','TR-261028-QWKJVF23',NULL,4,'2026-10-28 10:39:35'),(4,1,2,'reserve','ORD-261028-J09E4XCN',NULL,9,'2026-10-28 10:39:36'),(5,1,-2,'sale','ORD-261028-J09E4XCN',NULL,5,'2026-10-28 10:39:38'),(6,1,1,'return','RET-261028-P8SE3ZTY',NULL,5,'2026-10-28 10:39:40');
/*!40000 ALTER TABLE `stock_movements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stock_transfers`
--

DROP TABLE IF EXISTS `stock_transfers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stock_transfers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `transfer_no` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `from_warehouse_id` int NOT NULL,
  `to_warehouse_id` int NOT NULL,
  `product_id` int NOT NULL,
  `variant_id` int DEFAULT NULL,
  `quantity` int NOT NULL,
  `dispatched_qty` int DEFAULT NULL,
  `received_qty` int DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `note` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `transfer_no` (`transfer_no`),
  KEY `from_warehouse_id` (`from_warehouse_id`),
  KEY `product_id` (`product_id`),
  KEY `to_warehouse_id` (`to_warehouse_id`),
  KEY `variant_id` (`variant_id`),
  CONSTRAINT `stock_transfers_ibfk_1` FOREIGN KEY (`from_warehouse_id`) REFERENCES `warehouses` (`id`),
  CONSTRAINT `stock_transfers_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `stock_transfers_ibfk_3` FOREIGN KEY (`to_warehouse_id`) REFERENCES `warehouses` (`id`),
  CONSTRAINT `stock_transfers_ibfk_4` FOREIGN KEY (`variant_id`) REFERENCES `product_variants` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock_transfers`
--

LOCK TABLES `stock_transfers` WRITE;
/*!40000 ALTER TABLE `stock_transfers` DISABLE KEYS */;
INSERT INTO `stock_transfers` VALUES (1,'TR-261028-QWKJVF23',1,2,1,NULL,3,3,3,'received',NULL,4,'2026-10-28 10:39:35','2026-10-28 10:39:35');
/*!40000 ALTER TABLE `stock_transfers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `supplier_invoices`
--

DROP TABLE IF EXISTS `supplier_invoices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `supplier_invoices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `supplier_id` int NOT NULL,
  `po_id` int NOT NULL,
  `invoice_number` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `invoice_date` date DEFAULT NULL,
  `amount` decimal(12,2) NOT NULL,
  `paid_amount` decimal(12,2) DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_supplier_invoice` (`supplier_id`,`invoice_number`),
  KEY `po_id` (`po_id`),
  CONSTRAINT `supplier_invoices_ibfk_1` FOREIGN KEY (`po_id`) REFERENCES `purchase_orders` (`id`),
  CONSTRAINT `supplier_invoices_ibfk_2` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `supplier_invoices`
--

LOCK TABLES `supplier_invoices` WRITE;
/*!40000 ALTER TABLE `supplier_invoices` DISABLE KEYS */;
INSERT INTO `supplier_invoices` VALUES (1,2,1,'INV-530','2026-10-26',14000.00,0.00,'unpaid','2026-10-28 10:39:42');
/*!40000 ALTER TABLE `supplier_invoices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `supplier_products`
--

DROP TABLE IF EXISTS `supplier_products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `supplier_products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `supplier_id` int DEFAULT NULL,
  `product_id` int DEFAULT NULL,
  `cost_price` decimal(12,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_supplier_product` (`supplier_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `supplier_products_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `supplier_products_ibfk_2` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `supplier_products`
--

LOCK TABLES `supplier_products` WRITE;
/*!40000 ALTER TABLE `supplier_products` DISABLE KEYS */;
/*!40000 ALTER TABLE `supplier_products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suppliers`
--

DROP TABLE IF EXISTS `suppliers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suppliers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `kind` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contact_name` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `gst_number` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` text COLLATE utf8mb4_unicode_ci,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suppliers`
--

LOCK TABLES `suppliers` WRITE;
/*!40000 ALTER TABLE `suppliers` DISABLE KEYS */;
INSERT INTO `suppliers` VALUES (1,'Tech Distributors','supplier','Kiran','sales@techdistributors.in','9123456780','36ABCDE1234F1Z5',NULL,'approved','2026-10-28 09:00:49','2026-10-28 09:00:49'),(2,'Gadget Wholesale','supplier',NULL,'gw444@test.com','9000011111',NULL,NULL,'approved','2026-10-28 10:39:41','2026-10-28 10:39:41');
/*!40000 ALTER TABLE `suppliers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `support_tickets`
--

DROP TABLE IF EXISTS `support_tickets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `support_tickets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ticket_no` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_id` int NOT NULL,
  `order_id` int DEFAULT NULL,
  `product_id` int DEFAULT NULL,
  `subject` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `priority` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `assigned_to` int DEFAULT NULL,
  `resolution` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime DEFAULT NULL,
  `resolved_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ticket_no` (`ticket_no`),
  KEY `assigned_to` (`assigned_to`),
  KEY `order_id` (`order_id`),
  KEY `product_id` (`product_id`),
  KEY `ix_support_tickets_user_id` (`user_id`),
  CONSTRAINT `support_tickets_ibfk_1` FOREIGN KEY (`assigned_to`) REFERENCES `users` (`id`),
  CONSTRAINT `support_tickets_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `support_tickets_ibfk_3` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `support_tickets_ibfk_4` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `support_tickets`
--

LOCK TABLES `support_tickets` WRITE;
/*!40000 ALTER TABLE `support_tickets` DISABLE KEYS */;
INSERT INTO `support_tickets` VALUES (1,'TKT-261028-597YMAX9',9,NULL,NULL,'Delivery delay','resolved','high',6,'Delivered today','2026-10-28 10:39:40','2026-10-28 10:39:40');
/*!40000 ALTER TABLE `support_tickets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tax_rates`
--

DROP TABLE IF EXISTS `tax_rates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tax_rates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `rate` decimal(5,2) NOT NULL,
  `product_id` int DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `tax_rates_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE,
  CONSTRAINT `tax_rates_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tax_rates`
--

LOCK TABLES `tax_rates` WRITE;
/*!40000 ALTER TABLE `tax_rates` DISABLE KEYS */;
INSERT INTO `tax_rates` VALUES (1,'GST 18%',18.00,NULL,1,1,'2026-10-28 09:00:49'),(2,'GST 18% Mobiles',18.00,NULL,2,1,'2026-10-28 09:00:49'),(3,'GST 5% Apparel',5.00,NULL,4,1,'2026-10-28 09:00:49');
/*!40000 ALTER TABLE `tax_rates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `threshold_history`
--

DROP TABLE IF EXISTS `threshold_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `threshold_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inventory_id` int DEFAULT NULL,
  `old_value` int DEFAULT NULL,
  `new_value` int DEFAULT NULL,
  `changed_by` int DEFAULT NULL,
  `changed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inventory_id` (`inventory_id`),
  CONSTRAINT `threshold_history_ibfk_1` FOREIGN KEY (`inventory_id`) REFERENCES `inventory` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `threshold_history`
--

LOCK TABLES `threshold_history` WRITE;
/*!40000 ALTER TABLE `threshold_history` DISABLE KEYS */;
INSERT INTO `threshold_history` VALUES (1,1,5,10,4,'2026-10-28 10:39:35');
/*!40000 ALTER TABLE `threshold_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ticket_messages`
--

DROP TABLE IF EXISTS `ticket_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ticket_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ticket_id` int DEFAULT NULL,
  `sender_id` int DEFAULT NULL,
  `message` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_internal` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sender_id` (`sender_id`),
  KEY `ticket_id` (`ticket_id`),
  CONSTRAINT `ticket_messages_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`),
  CONSTRAINT `ticket_messages_ibfk_2` FOREIGN KEY (`ticket_id`) REFERENCES `support_tickets` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ticket_messages`
--

LOCK TABLES `ticket_messages` WRITE;
/*!40000 ALTER TABLE `ticket_messages` DISABLE KEYS */;
INSERT INTO `ticket_messages` VALUES (1,1,9,'Order not received',0,'2026-10-28 10:39:40'),(2,1,6,'Assigned to Sana Support',1,'2026-10-28 10:39:40'),(3,1,6,'Checking now',0,'2026-10-28 10:39:40');
/*!40000 ALTER TABLE `ticket_messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tracking_events`
--

DROP TABLE IF EXISTS `tracking_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tracking_events` (
  `id` int NOT NULL AUTO_INCREMENT,
  `shipment_id` int DEFAULT NULL,
  `status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `location` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_exception` tinyint(1) DEFAULT NULL,
  `source` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `event_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_tracking_events_shipment_id` (`shipment_id`),
  CONSTRAINT `tracking_events_ibfk_1` FOREIGN KEY (`shipment_id`) REFERENCES `shipments` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tracking_events`
--

LOCK TABLES `tracking_events` WRITE;
/*!40000 ALTER TABLE `tracking_events` DISABLE KEYS */;
INSERT INTO `tracking_events` VALUES (1,1,'created',NULL,'Shipment created',0,'manual','2026-10-28 10:39:38'),(2,1,'dispatched',NULL,'Handed to courier',0,'manual','2026-10-28 10:39:38'),(3,1,'in_transit','Pune hub',NULL,0,'manual','2026-10-28 10:39:39'),(4,1,'out_for_delivery','Hyderabad',NULL,0,'provider','2026-10-28 10:39:39'),(5,1,'out_for_delivery',NULL,'Attempt 1 failed: Customer not home',0,'manual','2026-10-28 10:39:39'),(6,1,'delivered',NULL,'Received by Ravi',0,'manual','2026-10-28 10:39:39');
/*!40000 ALTER TABLE `tracking_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_activities`
--

DROP TABLE IF EXISTS `user_activities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_activities` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `action` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `detail` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_user_activities_user_id` (`user_id`),
  CONSTRAINT `user_activities_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_activities`
--

LOCK TABLES `user_activities` WRITE;
/*!40000 ALTER TABLE `user_activities` DISABLE KEYS */;
INSERT INTO `user_activities` VALUES (1,9,'login',NULL,'2026-10-28 10:39:23'),(2,10,'login',NULL,'2026-10-28 10:39:23'),(3,2,'login',NULL,'2026-10-28 10:39:24'),(4,3,'login',NULL,'2026-10-28 10:39:25'),(5,4,'login',NULL,'2026-10-28 10:39:26'),(6,5,'login',NULL,'2026-10-28 10:39:26'),(7,6,'login',NULL,'2026-10-28 10:39:27'),(8,7,'login',NULL,'2026-10-28 10:39:28'),(9,8,'login',NULL,'2026-10-28 10:39:29'),(10,11,'register',NULL,'2026-10-28 10:39:29'),(11,11,'email_verified',NULL,'2026-10-28 10:39:30'),(12,12,'status_changed','active -> suspended by user 2','2026-10-28 10:39:32'),(13,9,'profile_update','full_name','2026-10-28 10:39:32');
/*!40000 ALTER TABLE `user_activities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `full_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role_id` int NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `registration_status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_email_verified` tinyint(1) DEFAULT NULL,
  `email_verify_token` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_login_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  UNIQUE KEY `phone` (`phone`),
  KEY `role_id` (`role_id`),
  KEY `ix_users_email_verify_token` (`email_verify_token`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'superadmin@shopsphere.com','9000000001','Super Admin','$2b$12$x.lzjM3BBeWkUGl7MHxTVOLBNCsVvscW0So9OuvaADEyCeTKSNEBm',1,'active','completed',1,NULL,NULL,'2026-10-28 09:00:47','2026-10-28 09:00:47'),(2,'admin@shopsphere.com','9000000002','Asha Admin','$2b$12$69A9.b6khz7qw4a3WJ/L0uRn./LYB8.aZylAKG8meBhhO6QYyK5w6',2,'active','completed',1,NULL,'2026-10-28 10:39:24','2026-10-28 09:00:47','2026-10-28 10:39:24'),(3,'products@shopsphere.com','9000000003','Pranav Products','$2b$12$AIXCqD9QJVVPS.LreNlrR.stBJfoM3mgSFT1WNAv6dsz8XLDtTxBi',3,'active','completed',1,NULL,'2026-10-28 10:39:25','2026-10-28 09:00:47','2026-10-28 10:39:25'),(4,'inventory@shopsphere.com','9000000004','Imran Inventory','$2b$12$ODSqF3TAl7B.TLSghuHcEOd/YOUwujcbOvnlBTEtBAgtlL9fzAvxy',4,'active','completed',1,NULL,'2026-10-28 10:39:26','2026-10-28 09:00:48','2026-10-28 10:39:26'),(5,'orders@shopsphere.com','9000000005','Olivia Orders','$2b$12$G7iKPjxm1bjuYvimJXKqEuvO7ibGJhmbQJ2LhfQ9RUTiCW89vzO.m',5,'active','completed',1,NULL,'2026-10-28 10:39:26','2026-10-28 09:00:48','2026-10-28 10:39:26'),(6,'support@shopsphere.com','9000000006','Sana Support','$2b$12$FEvWVP3Gw6It85siXA461OdnB6bg9Y4Nm2g.5HqAOlLg5ALMZjf0.',6,'active','completed',1,NULL,'2026-10-28 10:39:27','2026-10-28 09:00:48','2026-10-28 10:39:27'),(7,'delivery@shopsphere.com','9000000007','Dev Delivery','$2b$12$x47f2SVklGVd1alwgr9mv.yqVq.8qdWA9Ovld.U.6Rq3Z0vUhJXVW',8,'active','completed',1,NULL,'2026-10-28 10:39:28','2026-10-28 09:00:48','2026-10-28 10:39:28'),(8,'finance@shopsphere.com','9000000008','Farhan Finance','$2b$12$nQhfHjMSFmov9XrL7rDUJugTT780pK.WfDxpHH6CZEoSBtV8FpuCO',9,'active','completed',1,NULL,'2026-10-28 10:39:29','2026-10-28 09:00:48','2026-10-28 10:39:29'),(9,'customer@shopsphere.com','9876543210','Ravi Kumar','$2b$12$X9XcQiwvK/aNBCIprQr3uOG9G7wYxaShwxGzm45pJ4C63vrmPe0Om',7,'active','completed',1,NULL,'2026-10-28 10:39:22','2026-10-28 09:00:49','2026-10-28 10:39:32'),(10,'customer2@shopsphere.com','9876543211','Meena Customer','$2b$12$vAZWUTjIok7kWxKfqoHCuuMd6XXCf1UyjuIw1H8dVlVzBuYEvS7vq',7,'active','completed',1,NULL,'2026-10-28 10:39:23','2026-10-28 09:00:49','2026-10-28 10:39:23'),(11,'postman397@test.com','9827712345','Postman User','$2b$12$gXXO9oqnpYyoCM2hDF0Te.xVFF02sT3nzoOCAjgWnJxSLOPQHUBaC',7,'active','completed',1,NULL,NULL,'2026-10-28 10:39:29','2026-10-28 10:39:30'),(12,'agent950@shopsphere.com',NULL,'New Agent','$2b$12$bsb1Ltb32ZQCLLRXr/J4butLHQhsvDLDk6E9CcqTOqhgcDUEbhyPy',5,'suspended','completed',1,NULL,NULL,'2026-10-28 10:39:32','2026-10-28 10:39:32');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `warehouses`
--

DROP TABLE IF EXISTS `warehouses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warehouses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `city` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `capacity` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warehouses`
--

LOCK TABLES `warehouses` WRITE;
/*!40000 ALTER TABLE `warehouses` DISABLE KEYS */;
INSERT INTO `warehouses` VALUES (1,'Hyderabad Main','HYD01','Hyderabad',50000,1,'2026-10-28 09:00:49'),(2,'Bengaluru Hub','BLR01','Bengaluru',20000,1,'2026-10-28 09:00:49');
/*!40000 ALTER TABLE `warehouses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wishlist_items`
--

DROP TABLE IF EXISTS `wishlist_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wishlist_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `product_id` int NOT NULL,
  `added_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_wishlist` (`user_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `wishlist_items_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `wishlist_items_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wishlist_items`
--

LOCK TABLES `wishlist_items` WRITE;
/*!40000 ALTER TABLE `wishlist_items` DISABLE KEYS */;
INSERT INTO `wishlist_items` VALUES (1,9,2,'2026-10-28 10:39:36');
/*!40000 ALTER TABLE `wishlist_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'shopsphere'
--
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-28 16:17:26
