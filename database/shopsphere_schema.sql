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

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '351d6b62-842a-11f1-892b-b8f7759eda2b:1-4081';

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
) ENGINE=InnoDB AUTO_INCREMENT=118 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

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
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-28 16:17:47
