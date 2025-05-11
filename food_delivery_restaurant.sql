-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: food_delivery_restaurant
-- ------------------------------------------------------
-- Server version	8.0.42

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

--
-- Table structure for table `branches`
--

DROP TABLE IF EXISTS `branches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `branches` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `address` text,
  `latitude` decimal(9,6) NOT NULL,
  `longitude` decimal(9,6) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `branches`
--

LOCK TABLES `branches` WRITE;
/*!40000 ALTER TABLE `branches` DISABLE KEYS */;
INSERT INTO `branches` VALUES (1,'TDT Restaurant','19 Nguyen Huu Tho, District 7, Ho Chi Minh City, Vietnam',10.732005,106.699174,'2025-05-03 15:18:41',NULL),(3,'Lotteria Restaurant','Nguyen Thi Thap, District 7, Ho Chi Minh City, Vietnam',10.740784,106.702044,'2025-05-08 09:39:23','2025-05-09 16:22:03');
/*!40000 ALTER TABLE `branches` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `delivery_requests`
--

DROP TABLE IF EXISTS `delivery_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `delivery_requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `branch_id` int NOT NULL,
  `customer_id` int NOT NULL,
  `driver_id` int DEFAULT NULL,
  `status` enum('pending','delivering','delivered') NOT NULL DEFAULT 'pending',
  `dropoff_lat` decimal(9,6) NOT NULL,
  `dropoff_lon` decimal(9,6) NOT NULL,
  `distance_km` decimal(5,3) NOT NULL DEFAULT '0.000',
  `shipping_fee` decimal(12,3) NOT NULL DEFAULT '0.000',
  `is_forced_assignment` tinyint(1) NOT NULL DEFAULT '0',
  `is_active` tinyint(1) DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `assigned_at` datetime DEFAULT NULL,
  `accepted_at` datetime DEFAULT NULL,
  `picked_up_at` datetime DEFAULT NULL,
  `delivered_at` datetime DEFAULT NULL,
  `is_confirmed_by_customer` tinyint(1) NOT NULL DEFAULT '0',
  `is_confirmed_by_driver` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_id` (`order_id`),
  KEY `branch_id` (`branch_id`),
  KEY `customer_id` (`customer_id`),
  KEY `driver_id` (`driver_id`),
  CONSTRAINT `delivery_requests_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `delivery_requests_ibfk_2` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`),
  CONSTRAINT `delivery_requests_ibfk_3` FOREIGN KEY (`customer_id`) REFERENCES `users` (`id`),
  CONSTRAINT `delivery_requests_ibfk_4` FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delivery_requests`
--

LOCK TABLES `delivery_requests` WRITE;
/*!40000 ALTER TABLE `delivery_requests` DISABLE KEYS */;
INSERT INTO `delivery_requests` VALUES (1,1,3,3,2,'delivered',10.719858,106.700682,2.554,2.766,1,1,'2025-05-10 11:00:16','2025-05-10 11:02:03',NULL,'2025-05-10 11:03:47','2025-05-10 11:03:51',1,1),(2,2,3,3,3,'pending',10.719858,106.700682,2.554,2.766,0,1,'2025-05-10 11:05:30',NULL,'2025-05-10 11:08:22',NULL,NULL,0,0);
/*!40000 ALTER TABLE `delivery_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `drivers`
--

DROP TABLE IF EXISTS `drivers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drivers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `branch_id` int NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`branch_id`),
  KEY `branch_id` (`branch_id`),
  CONSTRAINT `drivers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `drivers_ibfk_2` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drivers`
--

LOCK TABLES `drivers` WRITE;
/*!40000 ALTER TABLE `drivers` DISABLE KEYS */;
INSERT INTO `drivers` VALUES (1,5,1,1,'2025-05-05 15:35:12'),(2,7,3,1,'2025-05-09 10:48:52'),(3,8,3,1,'2025-05-09 10:51:41');
/*!40000 ALTER TABLE `drivers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `kitchen_staffs`
--

DROP TABLE IF EXISTS `kitchen_staffs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kitchen_staffs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `branch_id` int NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`branch_id`),
  KEY `branch_id` (`branch_id`),
  CONSTRAINT `kitchen_staffs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `kitchen_staffs_ibfk_2` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kitchen_staffs`
--

LOCK TABLES `kitchen_staffs` WRITE;
/*!40000 ALTER TABLE `kitchen_staffs` DISABLE KEYS */;
INSERT INTO `kitchen_staffs` VALUES (1,4,1,1,'2025-05-04 18:27:48'),(4,9,3,1,'2025-05-09 10:53:01'),(5,10,3,1,'2025-05-09 10:53:11');
/*!40000 ALTER TABLE `kitchen_staffs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_items`
--

DROP TABLE IF EXISTS `menu_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `branch_id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text,
  `price` decimal(12,3) NOT NULL,
  `is_available` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `branch_id` (`branch_id`),
  CONSTRAINT `menu_items_ibfk_1` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_items`
--

LOCK TABLES `menu_items` WRITE;
/*!40000 ALTER TABLE `menu_items` DISABLE KEYS */;
INSERT INTO `menu_items` VALUES (2,1,'Margherita Pizza','Classic Italian pizza topped with fresh tomatoes, mozzarella cheese, and basil leaves.',12.990,1,'2025-05-05 18:20:56',NULL),(4,3,'Spaghetti Carbonara','Traditional Roman pasta dish made with eggs, Pecorino Romano cheese, guanciale, and black pepper.',14.500,1,'2025-05-08 09:43:20',NULL);
/*!40000 ALTER TABLE `menu_items` ENABLE KEYS */;
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
  `menu_item_id` int NOT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  `price` decimal(12,3) NOT NULL DEFAULT '0.000',
  `ks_id` int DEFAULT NULL,
  `status` enum('preparing','ready') DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  KEY `menu_item_id` (`menu_item_id`),
  KEY `ks_id` (`ks_id`),
  CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`menu_item_id`) REFERENCES `menu_items` (`id`),
  CONSTRAINT `order_items_ibfk_3` FOREIGN KEY (`ks_id`) REFERENCES `kitchen_staffs` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES (1,1,4,3,14.500,4,'ready','2025-05-10 11:00:14','2025-05-10 11:01:02'),(2,2,4,1,14.500,5,'ready','2025-05-10 11:05:28','2025-05-10 11:07:28');
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `branch_id` int NOT NULL,
  `status` enum('pending','preparing','ready_for_delivery') NOT NULL DEFAULT 'pending',
  `total_amount` decimal(12,3) NOT NULL DEFAULT '0.000',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `customer_id` (`customer_id`),
  KEY `branch_id` (`branch_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `users` (`id`),
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,3,3,'ready_for_delivery',43.500,'2025-05-10 11:00:16','2025-05-10 11:01:03'),(2,3,3,'ready_for_delivery',14.500,'2025-05-10 11:05:29','2025-05-10 11:07:28');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
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
  `customer_id` int NOT NULL,
  `total_order_amount` decimal(12,3) DEFAULT NULL,
  `shipping_fee` decimal(12,3) DEFAULT NULL,
  `total_amount` decimal(12,3) DEFAULT NULL,
  `method` enum('e_wallet','credit_card','bank_transfer') DEFAULT NULL,
  `status` enum('pending','paid','failed') NOT NULL DEFAULT 'pending',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_id` (`order_id`),
  KEY `customer_id` (`customer_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
INSERT INTO `payments` VALUES (1,1,3,43.500,2.766,46.266,'e_wallet','paid','2025-05-10 11:00:16','2025-05-10 11:00:29'),(2,2,3,14.500,2.766,17.266,'e_wallet','paid','2025-05-10 11:05:30','2025-05-10 11:05:52');
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `username` varchar(100) NOT NULL,
  `hashed_password` varchar(60) NOT NULL,
  `role` enum('customer','kitchen_staff','driver','owner','admin') NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin@gmail.com','admin','$2b$12$5AQU08FRMMm/sKSyQ06qPOZ.howL9fIWP.Km075jmgWSUB49IynvG','admin',1,'2025-05-02 16:41:39',NULL),(2,'owner@gmail.com','owner','$2b$12$2PpZt6idYwlGB2tMFMOP5OJRna72Hi7f4pHaEh1kaR3xqxiPEfZ46','owner',1,'2025-05-02 16:41:39',NULL),(3,'customer1@gmail.com','customer1','$2b$12$h1X2Fkhcep4BmAcgpMLAx.OrvS5LucrNCIsmZoTvxeBNvr5rTp0Yy','customer',1,'2025-05-04 18:05:06','2025-05-05 14:59:07'),(4,'kitchen_staff1@example.com','kitchen_staff1','$2b$12$pMBXtyi7EWoUsatk3PghC.vVzMVHhs4xWdsqW9cmf7McSSXCClUyy','kitchen_staff',1,'2025-05-04 18:26:53',NULL),(5,'driver1@gmail.com','driver1','$2b$12$5iIxr14c5arvZK4pHesp1OPAr4xLkHieQI1vdqggp8KO2oAGpk0oW','driver',1,'2025-05-05 08:31:44','2025-05-05 15:32:39'),(7,'driver2@example.com','driver2','$2b$12$2Tb5YT9E8zssYGDjo0A/tuF.QQ9vpLT1s561MIw7BcEYdWwAC4CMK','driver',1,'2025-05-09 10:38:28','2025-05-09 10:47:39'),(8,'driver3@example.com','driver3','$2b$12$VRtnB7gBRxvEO8fo1ie.heuvXYU.YQPgRxLt.vOvKiay2rb1/Li3y','driver',1,'2025-05-09 10:49:26','2025-05-09 10:51:16'),(9,'kitchen_staff2@example.com','kitchen_staff2','$2b$12$lWPUMgERjW50LWQXm9RpIOYmzqmSGgSYvoxiwsNAq0Dm46R65tyJS','kitchen_staff',1,'2025-05-09 10:52:30',NULL),(10,'kitchen_staff3@example.com','kitchen_staff3','$2b$12$u4p457I7rgxcuebJpM0ouuxSaqHxlNLHWa9uWHmt8HuNQjnln/wgm','kitchen_staff',1,'2025-05-09 10:52:43',NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-10 12:23:15
