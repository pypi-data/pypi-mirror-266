-- MySQL dump 10.13  Distrib 8.0.22, for Win64 (x86_64)
--
-- Host: localhost    Database: cheltuieli_desktop
-- ------------------------------------------------------
-- Server version	8.0.22

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
-- Table structure for table `aeroclub`
--

DROP TABLE IF EXISTS `aeroclub`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `aeroclub` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `valid_from` date NOT NULL,
  `valid_to` date DEFAULT NULL,
  `value` decimal(10,5) DEFAULT NULL,
  `pay_day` int DEFAULT NULL,
  `freq` int DEFAULT NULL,
  `auto_ext` tinyint(1) DEFAULT NULL,
  `myconto` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aeroclub`
--

LOCK TABLES `aeroclub` WRITE;
/*!40000 ALTER TABLE `aeroclub` DISABLE KEYS */;
INSERT INTO `aeroclub` VALUES (12,'BE_Jahresbeitrag','2018-02-22','2021-08-17',-439.30000,1,12,0,'EC'),(14,'BE_Jahresbeitrag','2021-07-01','2023-12-31',-439.30000,1,12,0,'DeutscheBank'),(19,'BE_ Qabrechnung','2021-04-01','2021-06-30',-232.33000,1,12,0,'EC'),(20,'BE_ Qabrechnung','2021-10-01','2022-01-31',-110.50000,1,3,0,'DeutscheBank'),(21,'BE_Jahresbeitrag','2024-01-01',NULL,-439.30000,1,12,1,'DeutscheBank');
/*!40000 ALTER TABLE `aeroclub` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alimentari`
--

DROP TABLE IF EXISTS `alimentari`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alimentari` (
  `#` int NOT NULL AUTO_INCREMENT,
  `data` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `type` varchar(50) DEFAULT NULL,
  `brutto` float NOT NULL,
  `amount` float NOT NULL,
  `ppu` float DEFAULT NULL,
  `km` int DEFAULT NULL,
  PRIMARY KEY (`#`)
) ENGINE=InnoDB AUTO_INCREMENT=587 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alimentari`
--

LOCK TABLES `alimentari` WRITE;
/*!40000 ALTER TABLE `alimentari` DISABLE KEYS */;
INSERT INTO `alimentari` VALUES (1,'2022-02-25 23:00:00','benzina',61.21,33.65,NULL,21894),(2,'2022-04-04 22:00:00','benzina',51.35,26.08,NULL,22668),(3,'2022-04-05 22:00:00','benzina',61.74,30.43,NULL,NULL),(4,'2022-04-23 22:00:00','benzina',70.07,35.23,NULL,NULL),(5,'2022-06-10 22:00:00','benzina',69.58,33.1,NULL,NULL),(6,'2022-06-10 22:00:00','benzina',30.06,14.89,NULL,NULL),(7,'2022-06-24 22:00:00','benzina',71.82,38.02,NULL,NULL),(8,'2022-06-28 22:00:00','benzina',30,14.97,NULL,NULL),(9,'2022-07-18 22:00:00','benzina',62.0479,33.74,NULL,NULL),(10,'2022-08-21 22:00:00','benzina',20.13,11.19,NULL,NULL),(11,'2022-08-21 22:00:00','benzina',35.92,20,NULL,NULL),(12,'2022-08-22 22:00:00','benzina',38.97,25.6206,NULL,NULL),(13,'2022-08-27 22:00:00','benzina',41.82,27.2403,NULL,NULL),(14,'2022-09-06 22:00:00','benzina',52.12,35.2606,NULL,NULL),(15,'2022-09-28 22:00:00','benzina',29.12,21.54,NULL,NULL),(16,'2022-09-29 22:00:00','benzina',29.84,22.21,NULL,NULL),(17,'2022-09-30 22:00:00','benzina',49.15,29.1,NULL,NULL),(18,'2022-10-09 22:00:00','benzina',30,15.39,NULL,NULL),(19,'2022-11-02 23:00:00','benzina',58.65,32.6,NULL,NULL),(20,'2022-12-12 23:00:00','benzina',33.84,20.77,NULL,NULL),(21,'2022-12-22 23:00:00','benzina',53.42,32.99,NULL,NULL),(22,'2023-02-13 23:00:00','benzina',59.98,34.31,NULL,NULL),(23,'2021-12-06 23:00:00','SWM',3.34,8.78,NULL,NULL),(24,'2021-12-12 23:00:00','SWM',3.39,8.92,NULL,NULL),(25,'2021-12-15 23:00:00','SWM',2.67,7.03,NULL,NULL),(26,'2021-12-18 23:00:00','SWM',2.98,7.85,NULL,NULL),(27,'2021-12-23 23:00:00','SWM',3.18,8.37,NULL,NULL),(28,'2021-12-29 23:00:00','SWM',3.22,8.48,NULL,NULL),(29,'2022-01-03 23:00:00','SWM',2.98,7.85,NULL,NULL),(30,'2022-01-06 23:00:00','SWM',1.81,4.75,NULL,NULL),(31,'2022-01-08 23:00:00','SWM',2.88,7.57,NULL,NULL),(32,'2022-01-12 23:00:00','EnBW',3.39,8.09,NULL,NULL),(33,'2022-01-17 23:00:00','SWM',3.27,8.61,NULL,NULL),(34,'2022-01-22 23:00:00','SWM',3.18,8.36,NULL,NULL),(35,'2022-02-01 23:00:00','SWM',2.74,7.2,NULL,NULL),(36,'2022-02-05 23:00:00','SWM',3.06,8.06,NULL,NULL),(37,'2022-02-14 23:00:00','SWM',2.99,7.87,NULL,NULL),(38,'2022-02-18 23:00:00','SWM',2.01,5.3,NULL,NULL),(39,'2022-02-25 23:00:00','SWM',3.25,8.55,NULL,NULL),(40,'2022-03-03 23:00:00','SWM',3.21,8.46,NULL,NULL),(41,'2022-03-12 23:00:00','SWM',3.19,8.39,NULL,NULL),(42,'2022-03-15 23:00:00','SWM',3.2,8.42,NULL,NULL),(43,'2022-03-19 23:00:00','SWM',2.25,5.91,NULL,NULL),(44,'2022-03-22 23:00:00','SWM',3.12,8.21,NULL,NULL),(45,'2022-03-26 23:00:00','SWM',3.1,8.15,NULL,NULL),(46,'2022-03-29 22:00:00','EnBW',3.5,8.34,NULL,NULL),(47,'2022-04-03 22:00:00','EnBW',3.5,8.35,NULL,NULL),(48,'2022-04-04 22:00:00','EnBW',3.43,8.17,NULL,NULL),(49,'2022-04-05 22:00:00','SWM',4.1,8.36,NULL,NULL),(50,'2022-04-07 22:00:00','EnBW',2.79,6.65,NULL,NULL),(51,'2022-04-10 22:00:00','SWM',1.26,2.57,NULL,NULL),(52,'2022-04-23 22:00:00','SWM',4.06,8.28,NULL,NULL),(53,'2022-04-26 22:00:00','SWM',4.09,8.34,NULL,NULL),(54,'2022-05-01 22:00:00','EnBW',2.71,6.46,NULL,NULL),(55,'2022-05-03 22:00:00','EnBW',2.69,6.41,NULL,NULL),(56,'2022-05-08 22:00:00','EnBW',3.43,8.18,NULL,NULL),(57,'2022-05-13 22:00:00','EnBW',3.51,8.38,NULL,NULL),(58,'2022-05-18 22:00:00','EnBW',3.49,8.32,NULL,NULL),(59,'2022-05-19 22:00:00','EnBW',2.17,5.18,NULL,NULL),(60,'2022-05-20 22:00:00','EnBW',2.53,6.04,NULL,NULL),(61,'2022-05-24 22:00:00','EnBW',3.61,8.6,NULL,NULL),(62,'2022-05-26 22:00:00','SWM',4,8.16,NULL,NULL),(63,'2022-05-28 22:00:00','EnBW',0.02,0.05,NULL,NULL),(64,'2022-05-28 22:00:00','EnBW',3.43,8.19,NULL,NULL),(65,'2022-05-24 22:00:00','SWM',3.97,8.1,NULL,NULL),(66,'2022-07-01 22:00:00','SWM',4.17,8.52,NULL,NULL),(67,'2022-07-02 22:00:00','SWM',1.76,3.59,NULL,NULL),(68,'2022-07-16 22:00:00','SWM',4.04,8.25,NULL,NULL),(69,'2022-07-18 22:00:00','SWM',4.03,8.22,NULL,NULL),(70,'2022-07-22 22:00:00','SWM',4.03,8.23,NULL,NULL),(71,'2022-07-23 22:00:00','SWM',2.86,5.83,NULL,NULL),(72,'2022-08-09 22:00:00','SWM',4.07,8.3,NULL,NULL),(73,'2022-08-14 22:00:00','SWM',2.92,5.96,NULL,NULL),(74,'2022-08-18 22:00:00','SWM',4.11,8.39,NULL,NULL),(75,'2022-09-30 22:00:00','SWM',4.06,8.28,NULL,NULL),(76,'2022-10-11 22:00:00','SWM',1.99,4.07,NULL,NULL),(77,'2022-10-13 22:00:00','SWM',4.07,8.3,NULL,NULL),(78,'2022-10-22 22:00:00','SWM',4.16,8.49,NULL,NULL),(79,'2022-10-31 23:00:00','SWM',4.16,8.49,NULL,NULL),(80,'2022-11-16 23:00:00','SWM',2.67,5.44,NULL,NULL),(81,'2022-12-02 23:00:00','SWM',4.09,8.35,NULL,NULL),(82,'2022-12-05 23:00:00','SWM',2.18,4.44,NULL,NULL),(83,'2022-12-21 23:00:00','SWM',3.96,8.08,NULL,NULL),(84,'2022-12-30 23:00:00','SWM',2.78,5.67,NULL,NULL),(85,'2023-01-04 23:00:00','SWM',2.7,5.52,NULL,NULL),(86,'2023-01-06 23:00:00','SWM',3.94,8.04,NULL,NULL),(87,'2023-01-11 23:00:00','SWM',2.7,5.51,NULL,NULL),(88,'2023-01-15 23:00:00','SWM',3.46,7.07,NULL,NULL),(89,'2023-01-16 23:00:00','SWM',0.72,1.46,NULL,NULL),(90,'2022-05-31 22:00:00','EnBW',2.75,6.6,NULL,NULL),(91,'2022-06-02 22:00:00','EnBW',2.86,6.8,NULL,NULL),(92,'2022-06-06 22:00:00','EnBW',3.4,8.1,NULL,NULL),(93,'2022-06-08 22:00:00','EnBW',2.42,5.8,NULL,NULL),(94,'2022-06-13 22:00:00','EnBW',2.79,6.7,NULL,NULL),(95,'2022-06-16 22:00:00','EnBW',2.45,5.9,NULL,NULL),(96,'2022-06-23 22:00:00','EnBW',3.46,8.2,NULL,NULL),(97,'2022-06-28 22:00:00','EnBW',2.78,7.3,NULL,NULL),(98,'2022-06-28 22:00:00','EnBW',3.37,8,NULL,NULL),(99,'2022-07-07 22:00:00','EnBW',2.85,6.8,NULL,NULL),(100,'2022-07-15 22:00:00','EnBW',1.82,4.3,NULL,NULL),(101,'2022-07-21 22:00:00','EnBW',2.61,6.2,NULL,NULL),(102,'2022-07-29 22:00:00','EnBW',3.55,8.5,NULL,NULL),(103,'2022-07-30 22:00:00','EnBW',2.82,6.7,NULL,NULL),(104,'2022-08-01 22:00:00','EnBW',2.3,5.5,NULL,NULL),(105,'2022-08-04 22:00:00','EnBW',3.12,7.4,NULL,NULL),(106,'2022-08-06 22:00:00','EnBW',3.54,8.4,NULL,NULL),(107,'2022-08-11 22:00:00','EnBW',3.31,7.9,NULL,NULL),(108,'2022-08-13 22:00:00','EnBW',2.49,5.9,NULL,NULL),(109,'2022-08-17 22:00:00','EnBW',2.81,6.7,NULL,NULL),(110,'2022-08-20 22:00:00','EnBW',3.43,8.2,NULL,NULL),(111,'2022-10-05 22:00:00','EnBW',3.3,7.9,NULL,NULL),(112,'2022-10-06 22:00:00','EnBW',3.52,8.4,NULL,NULL),(113,'2022-10-08 22:00:00','EnBW',2.73,6.5,NULL,NULL),(114,'2022-10-09 22:00:00','EnBW',2.89,6.9,NULL,NULL),(115,'2022-10-11 22:00:00','EnBW',3.48,8.3,NULL,NULL),(116,'2022-10-12 22:00:00','EnBW',1.84,4.4,NULL,NULL),(117,'2022-10-18 22:00:00','EnBW',3.43,8.2,NULL,NULL),(118,'2022-10-25 22:00:00','EnBW',2.63,6.3,NULL,NULL),(119,'2022-11-03 23:00:00','EnBW',3.09,5.2,NULL,NULL),(120,'2022-11-08 23:00:00','EnBW',3.48,8.3,NULL,NULL),(121,'2022-11-14 23:00:00','EnBW',3.36,8,NULL,NULL),(122,'2022-11-18 23:00:00','EnBW',2.28,5.4,NULL,NULL),(123,'2022-11-27 23:00:00','EnBW',2.05,4.9,NULL,NULL),(124,'2022-02-07 23:00:00','EnBW',2.74,6.5,NULL,NULL),(125,'2022-12-11 23:00:00','EnBW',3.25,7.8,NULL,NULL),(126,'2022-12-12 23:00:00','EnBW',0.96,2.3,NULL,NULL),(127,'2022-12-14 23:00:00','EnBW',0.92,2.2,NULL,NULL),(128,'2022-12-18 23:00:00','EnBW',3.49,8.3,NULL,NULL),(129,'2022-12-26 23:00:00','EnBW',2.98,7.1,NULL,NULL),(130,'2023-01-02 23:00:00','EnBW',2.68,6.4,NULL,NULL),(131,'2022-01-08 23:00:00','EnBW',2.81,6.7,NULL,NULL),(132,'2022-01-16 23:00:00','EnBW',5.03,8.1,NULL,NULL),(133,'2023-01-24 23:00:00','eCharge',4.47,8.443,NULL,NULL),(134,'2023-02-15 23:00:00','eCharge',3.45,6.229,NULL,NULL),(142,'2023-02-02 00:00:00','SWM',3.39,6.91,NULL,NULL),(152,'2023-02-11 00:00:00','SWM',3.05,6.23,NULL,NULL),(162,'2023-02-17 00:00:00','SWM',1.08,2.2,NULL,NULL),(172,'2023-02-24 00:00:00','SWM',3.91,7.97,NULL,NULL),(212,'2023-03-09 00:00:00','benzina',60.22,33.85,NULL,37696),(222,'2023-02-27 00:00:00','eCharge',4.28,8.11,NULL,NULL),(232,'2023-03-10 00:00:00','eCharge',4.31,8.11,NULL,NULL),(242,'2023-01-09 00:00:00','EnBW',2.81,6.7,NULL,NULL),(252,'2023-01-17 00:00:00','EnBW',5.03,8.1,NULL,NULL),(261,'2023-03-25 00:00:00','benzina',48.59,28.43,1.709,38429),(271,'2023-03-25 00:00:00','EnBW',3.72,6,0.62,0),(281,'2023-03-02 00:00:00','SWM',4.07,8.31,0.49,0),(291,'2023-03-05 00:00:00','SWM',3.93,8.02,0.49,0),(301,'2023-03-15 00:00:00','SWM',1.23,2.5,0.492,0),(311,'2023-03-16 00:00:00','SWM',2.95,6.02,0.49,0),(321,'2023-03-19 00:00:00','SWM',3.48,7.1,0.49,0),(331,'2023-03-20 00:00:00','SWM',3.12,6.37,0.49,0),(341,'2023-03-23 00:00:00','SWM',4.14,8.44,0.491,0),(351,'2023-03-26 00:00:00','SWM',4.02,8.2,0.49,0),(361,'2023-03-30 00:00:00','SWM',4.12,8.4,0.49,0),(371,'2023-04-01 00:00:00','SWM',3.07,5.2,0.59,0),(381,'2023-04-05 00:00:00','SWM',4.37,7.41,0.59,0),(391,'2023-04-08 00:00:00','SWM',4.19,7.1,0.59,0),(401,'2023-04-10 00:00:00','SWM',4.73,8.01,0.591,0),(421,'2023-04-15 00:00:00','benzina',68.6,37.1,1.849,39318),(431,'2023-04-17 00:00:00','benzina',44.44,27.57,1.612,39862),(441,'2023-04-17 00:00:00','benzina',17.47,10.81,1.616,40074),(451,'2023-04-27 00:00:00','benzina',47.41,29.92,1.585,40734),(461,'2023-05-02 00:00:00','benzina',63.38,35.23,1.799,41516),(471,'2023-04-25 00:00:00','EnBW',4.9,7.9,0.62,0),(481,'2023-04-28 00:00:00','EnBW',3.93,6.3,0.624,0),(491,'2023-04-14 00:00:00','SWM',4.86,8.23,0.591,0),(501,'2023-06-09 00:00:00','benzina',62.03,34.87,1.779,42732),(511,'2023-07-04 00:00:00','benzina',49.04,27.41,1.789,43809),(521,'2023-08-12 00:00:00','benzina',30,16.4,1.829,44726),(531,'2023-09-15 22:00:00','benzina',69.41,36.17,1.919,45784),(532,'2023-10-02 22:00:00','benzina',43.06,24.48,1.759,46580),(533,'2023-11-01 23:00:00','benzina',61.43,33.77,1.819,47607),(534,'2023-04-18 22:00:00','MyHyundai',4.35,7.88,0.552,0),(535,'2023-04-28 22:00:00','MyHyundai',4.5,8.19,0.549,0),(536,'2023-05-01 22:00:00','MyHyundai',4.51,8.21,0.549,0),(537,'2023-05-05 22:00:00','MyHyundai',4.43,8.04,0.551,0),(538,'2023-05-12 22:00:00','MyHyundai',4.52,8.23,0.549,0),(539,'2023-05-14 22:00:00','MyHyundai',4.31,7.78,0.554,0),(540,'2023-05-16 22:00:00','MyHyundai',3.83,6.82,0.562,0),(541,'2023-05-19 22:00:00','MyHyundai',3.43,6,0.572,0),(542,'2023-05-23 22:00:00','MyHyundai',4.42,5.859,0.754,0),(543,'2023-05-26 22:00:00','MyHyundai',4.58,8.34,0.549,0),(544,'2023-05-28 22:00:00','MyHyundai',4.49,8.16,0.55,0),(545,'2023-05-31 22:00:00','MyHyundai',4.43,8.04,0.551,0),(546,'2023-06-02 22:00:00','MyHyundai',4.49,8.16,0.55,0),(547,'2023-06-08 22:00:00','MyHyundai',4.53,8.26,0.548,0),(548,'2023-06-10 22:00:00','MyHyundai',4.38,7.94,0.552,0),(549,'2023-06-16 22:00:00','MyHyundai',4.27,7.71,0.554,0),(550,'2023-06-17 22:00:00','MyHyundai',4.53,8.26,0.548,0),(551,'2023-06-23 22:00:00','MyHyundai',3.99,7.14,0.559,0),(552,'2023-06-24 22:00:00','MyHyundai',4.49,8.16,0.55,0),(553,'2023-06-26 22:00:00','MyHyundai',4.22,7.61,0.555,0),(554,'2023-07-01 22:00:00','MyHyundai',4.45,8.09,0.55,0),(555,'2023-07-03 22:00:00','MyHyundai',2.41,3.92,0.615,0),(556,'2023-07-12 22:00:00','MyHyundai',4.51,8.2,0.55,0),(557,'2023-07-15 22:00:00','MyHyundai',4.55,8.27,0.55,0),(558,'2023-07-18 22:00:00','MyHyundai',4.28,7.74,0.553,0),(559,'2023-07-20 22:00:00','MyHyundai',3.95,7.06,0.559,0),(560,'2023-07-29 22:00:00','MyHyundai',4.56,8.29,0.55,0),(561,'2023-07-31 22:00:00','MyHyundai',4.46,8.11,0.55,0),(562,'2023-08-03 22:00:00','MyHyundai',4.49,8.16,0.55,0),(563,'2023-08-07 22:00:00','MyHyundai',3.74,6.62,0.565,0),(564,'2023-08-10 22:00:00','MyHyundai',4.57,8.32,0.549,0),(565,'2023-08-11 22:00:00','MyHyundai',4.44,8.05,0.552,0),(566,'2023-08-13 22:00:00','MyHyundai',3.33,5.79,0.575,0),(567,'2023-08-23 22:00:00','MyHyundai',3.38,5.89,0.574,0),(568,'2023-08-24 22:00:00','MyHyundai',4.36,7.89,0.553,0),(569,'2023-09-04 22:00:00','MyHyundai',4.5,8.17,0.551,0),(570,'2023-09-06 22:00:00','MyHyundai',2.65,4.41,0.601,0),(571,'2023-09-09 22:00:00','MyHyundai',4.43,8.03,0.552,0),(572,'2023-09-12 22:00:00','MyHyundai',4.46,8.1,0.551,0),(573,'2023-09-17 22:00:00','MyHyundai',4.53,8.25,0.549,0),(574,'2023-09-18 22:00:00','MyHyundai',4.46,8.1,0.551,0),(575,'2023-09-19 22:00:00','MyHyundai',4.57,8.32,0.549,0),(576,'2023-09-23 22:00:00','MyHyundai',4.41,8,0.551,0),(577,'2023-09-26 22:00:00','MyHyundai',4.21,7.6,0.554,0),(578,'2023-09-28 22:00:00','MyHyundai',2.58,4.28,0.603,0),(579,'2023-10-06 22:00:00','MyHyundai',4.53,8.04,0.563,0),(580,'2023-10-09 22:00:00','MyHyundai',4.64,8.27,0.561,0),(581,'2023-10-11 22:00:00','MyHyundai',3.65,6.25,0.584,0),(582,'2023-10-13 22:00:00','MyHyundai',4.06,7.07,0.574,0),(583,'2023-10-18 22:00:00','MyHyundai',4.61,8.2,0.562,0),(584,'2023-10-22 22:00:00','MyHyundai',3.43,5.8,0.591,0),(585,'2023-10-26 22:00:00','MyHyundai',4.59,8.18,0.561,0),(586,'2023-10-03 22:00:00','SWM',4.66,7.84,0.594,0);
/*!40000 ALTER TABLE `alimentari` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `apartament`
--

DROP TABLE IF EXISTS `apartament`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartament` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `valid_from` date NOT NULL,
  `valid_to` date DEFAULT NULL,
  `value` decimal(10,5) DEFAULT NULL,
  `pay_day` int DEFAULT NULL,
  `freq` int DEFAULT NULL,
  `auto_ext` tinyint(1) DEFAULT NULL,
  `myconto` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartament`
--

LOCK TABLES `apartament` WRITE;
/*!40000 ALTER TABLE `apartament` DISABLE KEYS */;
INSERT INTO `apartament` VALUES (1,'ARD-ZDF','2019-05-15',NULL,-52.50000,15,3,1,'Siri&Radu'),(2,'PYUR','2017-11-08','2022-02-28',-28.00000,31,1,0,'Siri&Radu'),(3,'SWK','2020-11-02','2021-07-25',-73.00000,15,1,0,'Siri&Radu'),(4,'SWK','2021-07-25','2022-07-25',-49.00000,15,1,0,'Siri&Radu'),(5,'Miete_Königteinstr1','2020-10-01','2023-06-30',-1110.00000,31,1,0,'Siri&Radu'),(6,'Chiria_Garaj','2020-10-01','2022-04-30',-90.00000,31,1,0,'Siri&Radu'),(7,'Chiria_DachauerStr','2017-11-01','2020-11-15',-992.00000,30,1,0,'EC'),(8,'Miete_Garage 4','2022-05-31',NULL,-45.00000,31,1,1,'Siri&Radu'),(9,'Miete_Thief_Garaj','2022-05-01',NULL,-80.00000,30,1,1,'Siri&Radu'),(10,'SWK','2021-08-25','2023-03-31',-60.00000,15,1,0,'Siri&Radu'),(11,'PYUR','2022-03-31','2023-07-31',-25.50000,31,1,0,'Siri&Radu'),(12,'Miete_Königteinstr1','2023-07-01',NULL,-1200.00000,31,1,1,'Siri&Radu'),(13,'Vattenfall','2021-04-01',NULL,-54.00000,5,1,1,'Siri&Radu'),(14,'PYUR','2023-08-01',NULL,-28.00000,31,1,1,'Siri&Radu');
/*!40000 ALTER TABLE `apartament` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `asigurari`
--

DROP TABLE IF EXISTS `asigurari`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `asigurari` (
  `id` int NOT NULL AUTO_INCREMENT,
  `company` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `value` decimal(10,5) NOT NULL,
  `pay_day` int DEFAULT NULL,
  `valid_from` date NOT NULL,
  `valid_to` date DEFAULT NULL,
  `freq` int NOT NULL,
  `auto_ext` tinyint(1) DEFAULT NULL,
  `myconto` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `asigurari`
--

LOCK TABLES `asigurari` WRITE;
/*!40000 ALTER TABLE `asigurari` DISABLE KEYS */;
INSERT INTO `asigurari` VALUES (2,'Huk-Coburg','Auto-Versicherung',-799.59000,1,'2021-01-01','2021-12-31',12,0,'EC'),(3,'dieBayerische','Zahnzusatz-Versicherung',-32.60000,31,'2019-03-01','2022-02-28',1,0,'EC'),(4,'ADAC','ADAC-Membership',-94.00000,1,'2020-11-01','2021-10-31',12,0,'EC'),(5,'ADAC','ADAC-Reiserücktritts',-88.70000,1,'2021-07-28','2022-07-27',12,0,'EC'),(6,'VersicherungsKammerBayern','RisikoLebenVersicherung',-19.31000,31,'2018-09-01',NULL,1,1,'EC'),(7,'Huk-Coburg','Privathaftpflichtversicherung',-77.00000,1,'2020-11-20','2021-11-19',12,0,'Siri&Radu'),(8,'VersicherungsKammerBayern','Rechtsschutzversicherung',-277.20000,1,'2020-07-16','2023-07-16',12,1,'Siri&Radu'),(9,'Huk-Coburg','Unfallversicherung',-82.01000,1,'2020-12-23','2021-12-22',12,0,'EC'),(10,'Huk-Coburg','Hausratversicherung',-45.05000,1,'2020-11-06','2021-11-05',12,0,'Siri&Radu'),(15,'ADAC','ADAC-Membership',-94.00000,1,'2021-11-01','2022-10-31',12,1,'DeutscheBank'),(16,'Huk-Coburg','Auto-Versicherung',-660.60000,1,'2022-01-01','2022-12-31',12,0,'DeutscheBank'),(17,'ADAC','ADAC-Reiserücktritts',-88.70000,1,'2022-07-28',NULL,12,1,'Siri&Radu'),(18,'Huk-Coburg','Unfallversicherung',-84.96000,1,'2021-12-23','2022-12-22',12,0,'DeutscheBank'),(21,'Huk-Coburg','Hausratversicherung',-45.05000,1,'2021-11-06','2022-11-05',12,0,'Siri&Radu'),(23,'Huk-Coburg','Privathaftpflichtversicherung',-77.00000,1,'2021-11-20','2022-11-19',12,0,'Siri&Radu'),(24,'dieBayerische','Zahnzusatz-Versicherung',-35.20000,31,'2022-03-01','2023-02-28',1,0,'EC'),(25,'dieBayerische','Zahnzusatz-Versicherung',-41.20000,31,'2023-03-01',NULL,1,1,'EC'),(26,'Huk-Coburg','Auto-Versicherung',-692.71000,1,'2024-01-01','2024-12-31',12,1,'Siri&Radu'),(27,'Huk-Coburg','Unfallversicherung',-90.86000,1,'2023-12-23','2024-12-22',12,1,'Siri&Radu'),(28,'Huk-Coburg','Hausratversicherung',-49.56000,6,'2023-11-06','2024-11-05',12,1,'Siri&Radu'),(29,'Huk-Coburg','Privathaftpflichtversicherung',-77.00000,1,'2023-11-20','2024-11-19',12,1,'Siri&Radu');
/*!40000 ALTER TABLE `asigurari` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `banca`
--

DROP TABLE IF EXISTS `banca`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `banca` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `banca` varchar(50) NOT NULL,
  `valid_from` date NOT NULL,
  `valid_to` date DEFAULT NULL,
  `value` decimal(10,5) NOT NULL,
  `pay_day` int DEFAULT NULL,
  `freq` int NOT NULL,
  `myconto` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `banca`
--

LOCK TABLES `banca` WRITE;
/*!40000 ALTER TABLE `banca` DISABLE KEYS */;
INSERT INTO `banca` VALUES (1,'EC','Stadtsparkasse München','2018-01-03',NULL,0.00000,NULL,12,'EC'),(2,'Savings','Stadtsparkasse München','2018-01-01',NULL,0.00000,NULL,1,''),(3,'Siri&Radu','Stadtsparkasse München','2019-01-01',NULL,0.00000,NULL,1,'Siri&Radu'),(4,'Credit','Stadtsparkasse München','2018-01-30',NULL,0.00000,31,1,'EC'),(5,'MasterCard','Stadtsparkasse München','2018-01-01',NULL,-29.00000,1,12,'EC'),(6,'N26','N26','2018-01-01',NULL,0.00000,NULL,1,''),(7,'DeutscheBank','DeutscheBank','2018-01-01',NULL,0.00000,NULL,1,'');
/*!40000 ALTER TABLE `banca` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `expenses`
--

DROP TABLE IF EXISTS `expenses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `expenses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `valid_from` date NOT NULL,
  `valid_to` date DEFAULT NULL,
  `freq` int NOT NULL,
  `auto_ext` tinyint(1) DEFAULT NULL,
  `post_pay` tinyint(1) DEFAULT NULL,
  `value` decimal(10,5) NOT NULL,
  `pay_day` int DEFAULT NULL,
  `myconto` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `expenses`
--

LOCK TABLES `expenses` WRITE;
/*!40000 ALTER TABLE `expenses` DISABLE KEYS */;
INSERT INTO `expenses` VALUES (2,'MasterCard','2020-10-05',NULL,1,1,NULL,0.00000,4,'EC'),(5,'CartelaPrepaid','2020-10-15',NULL,2,1,NULL,-15.00000,15,'EC'),(6,'Siri&Radu_ENTGELTABSCHLUSS','2021-01-30','2023-10-31',1,0,NULL,-5.24000,31,'Siri&Radu'),(7,'EC_ENTGELTABSCHLUSS','2021-01-30',NULL,1,1,NULL,-2.25000,31,'EC'),(8,'ExtraCredit','2021-01-30','2023-08-31',1,0,NULL,-600.00000,5,'EC'),(9,'cash','2021-01-30',NULL,1,NULL,NULL,0.00000,NULL,'EC'),(10,'Credit','2021-01-30',NULL,1,1,NULL,-532.00000,30,'EC'),(11,'CreditMasina','2022-02-01',NULL,1,1,NULL,-138.60000,1,'EC'),(12,'Cresa_Enya','2023-01-01','2023-10-31',1,NULL,NULL,-335.00000,1,'Siri&Radu'),(13,'Kaution_Cresa_Enya','2023-01-01','2023-01-31',36,0,NULL,-750.00000,1,'Siri&Radu'),(14,'Spotify','2022-12-09','2023-12-31',1,0,NULL,-14.99000,1,'N26'),(15,'Netflix','2022-12-09','2023-05-31',1,0,NULL,-11.99000,1,'N26'),(16,'Siri&Radu_ENTGELTABSCHLUSS','2023-11-01',NULL,1,1,NULL,-4.95000,31,'Siri&Radu'),(17,'Cresa_Enya','2023-11-01',NULL,1,1,NULL,-215.00000,1,'Siri&Radu'),(18,'Spotify','2024-01-01',NULL,1,1,NULL,-17.99000,1,'N26'),(19,'Netflix','2023-06-01',NULL,1,1,NULL,-14.98000,1,'N26'),(20,'Heroku','2023-01-01',NULL,1,1,NULL,-7.00000,5,'N26');
/*!40000 ALTER TABLE `expenses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `income`
--

DROP TABLE IF EXISTS `income`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `income` (
  `id` int NOT NULL AUTO_INCREMENT,
  `company` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `hours` int DEFAULT NULL,
  `steuerklasse` int DEFAULT NULL,
  `valid_from` date NOT NULL,
  `valid_to` date DEFAULT NULL,
  `value` decimal(10,5) DEFAULT NULL,
  `pay_day` int DEFAULT NULL,
  `freq` int NOT NULL,
  `myconto` varchar(50) NOT NULL,
  `auto_ext` tinyint(1) DEFAULT NULL,
  `tax` varchar(25) DEFAULT NULL,
  `proc` decimal(10,5) DEFAULT NULL,
  `in_salary` tinyint NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `income`
--

LOCK TABLES `income` WRITE;
/*!40000 ALTER TABLE `income` DISABLE KEYS */;
INSERT INTO `income` VALUES (1,'MTU-AeroEngines','Salariu',35,3,'2022-02-01','2022-05-31',4837.00000,30,1,'EC',0,'salary',NULL,1),(7,'MTU-AeroEngines','T-Geld',0,NULL,'2022-02-27',NULL,NULL,30,12,'EC',0,'bonus',0.18400,1),(8,'MTU-AeroEngines','ErfolgsBeteiligung',0,NULL,'2022-04-30',NULL,3365.00000,30,12,'EC',0,'bonus',NULL,1),(9,'MTU-AeroEngines','UrlaubsGeld',0,NULL,'2019-06-30',NULL,NULL,30,12,'EC',1,'bonus',0.70000,1),(10,'MTU-AeroEngines','T-Zug B',0,NULL,'2022-07-30',NULL,610.00000,30,12,'EC',1,'bonus',NULL,1),(11,'MTU-AeroEngines','Weinachtsgeld',0,NULL,'2019-11-30',NULL,NULL,30,12,'EC',1,'bonus',0.55000,1),(12,'MTU-AeroEngines','MitarbeiterAktienProgram',0,NULL,'2022-05-01',NULL,923.85000,30,12,'EC',1,'bonus',NULL,1),(13,'StadtMünchen','KinderGeld',0,NULL,'2022-01-15','2022-12-31',219.00000,15,1,'Siri_Radu',NULL,NULL,NULL,0),(14,'StadtMünchen','FamilienGeld',0,NULL,'2023-01-15','2023-09-14',250.00000,15,1,'Siri_Radu',1,NULL,NULL,0),(15,'MTU-AeroEngines','Inflationsausgleichprämie',0,NULL,'2023-01-01','2023-01-30',1500.00000,30,12,'EC',1,NULL,NULL,1),(16,'MTU-AeroEngines','Salariu',40,3,'2022-06-01','2023-05-31',4837.00000,30,1,'EC',0,'salary',NULL,1),(17,'MTU-AeroEngines','Salariu',35,1,'2019-08-01','2022-01-31',4837.00000,30,1,'EC',0,'salary',NULL,1),(18,'MTU-AeroEngines','Salariu',40,3,'2023-06-01','2023-07-31',5089.00000,30,1,'EC',0,'salary',NULL,1),(20,'MTU-AeroEngines','Leistungszul',0,NULL,'2021-06-01',NULL,NULL,30,1,'EC',1,'salary',0.14000,1),(21,'MTU-AeroEngines','T-Zug A',0,NULL,'2022-07-30',NULL,NULL,30,12,'EC',1,'bonus',0.27500,1),(22,'MTU-AeroEngines','Salariu',40,4,'2023-08-01',NULL,5089.00000,30,1,'EC',1,'salary',NULL,1),(23,'StadtMünchen','KinderGeld',0,NULL,'2023-01-01','2040-01-15',250.00000,15,1,'Siri_Radu',1,NULL,NULL,0);
/*!40000 ALTER TABLE `income` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `intercontotrans`
--

DROP TABLE IF EXISTS `intercontotrans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `intercontotrans` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `valid_from` date NOT NULL,
  `valid_to` date DEFAULT NULL,
  `freq` int NOT NULL,
  `auto_ext` tinyint(1) DEFAULT NULL,
  `post_pay` tinyint(1) DEFAULT NULL,
  `value` decimal(10,5) NOT NULL,
  `pay_day` int DEFAULT NULL,
  `myconto` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `intercontotrans`
--

LOCK TABLES `intercontotrans` WRITE;
/*!40000 ALTER TABLE `intercontotrans` DISABLE KEYS */;
INSERT INTO `intercontotrans` VALUES (1,'chiria','2020-10-01',NULL,1,1,NULL,-1000.00000,30,'EC'),(4,'N26','2020-10-01',NULL,1,1,NULL,-500.00000,30,'EC');
/*!40000 ALTER TABLE `intercontotrans` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `one_time_transactions`
--

DROP TABLE IF EXISTS `one_time_transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `one_time_transactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `value` decimal(10,5) NOT NULL,
  `myconto` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `freq` int NOT NULL DEFAULT '1',
  `pay_day` int NOT NULL DEFAULT '1',
  `valid_from` date NOT NULL,
  `valid_to` date NOT NULL,
  `auto_ext` smallint DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `one_time_transactions`
--

LOCK TABLES `one_time_transactions` WRITE;
/*!40000 ALTER TABLE `one_time_transactions` DISABLE KEYS */;
INSERT INTO `one_time_transactions` VALUES (1,'Steuererklärung_2022',-2796.00000,'Siri&Radu',999,15,'2023-09-15','2023-09-15',NULL);
/*!40000 ALTER TABLE `one_time_transactions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stat`
--

DROP TABLE IF EXISTS `stat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stat` (
  `id` int NOT NULL AUTO_INCREMENT,
  `documente_id` int NOT NULL DEFAULT '8',
  `name` varchar(50) NOT NULL,
  `valid_from` date NOT NULL,
  `valid_to` date DEFAULT NULL,
  `value` decimal(10,5) DEFAULT NULL,
  `pay_day` int DEFAULT NULL,
  `freq` int DEFAULT NULL,
  `myconto` varchar(50) DEFAULT NULL,
  `auto_ext` tinyint(1) DEFAULT NULL,
  `post_pay` tinyint(1) DEFAULT NULL,
  `path` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stat`
--

LOCK TABLES `stat` WRITE;
/*!40000 ALTER TABLE `stat` DISABLE KEYS */;
INSERT INTO `stat` VALUES (4,8,'LOHNSTEUERHILFE BAY.','2021-01-01','2021-12-31',-242.00000,1,12,'EC',0,NULL,''),(6,8,'Kfz-Steuer fuer M RA 8612','2015-08-30','2021-11-30',-92.00000,1,12,'EC',0,NULL,''),(8,8,'LOHNSTEUERHILFE BAY.','2022-01-01','2022-01-31',-242.00000,1,12,'DeutscheBank',0,NULL,''),(9,8,'LOHNSTEUERHILFE BAY.','2023-01-01','2023-12-31',-380.00000,1,12,'Siri&Radu',0,NULL,''),(10,8,'Kfz-Steuer fuer M RA 8612','2021-12-01','2022-11-30',-2.00000,1,12,'EC',0,NULL,''),(11,8,'Kfz-Steuer fuer M-RS8622E','2022-12-01',NULL,-2.00000,1,12,'EC',1,NULL,'');
/*!40000 ALTER TABLE `stat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(250) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (5,'radu','radu@radu.com','pbkdf2:sha256:260000$wPBSTjoH4lG99fgg$c91fec5b5eeade9c9602a64a826d6e5715a86364523dae964cc0c989752d5801'),(6,'siri','siri@siri.de','pbkdf2:sha256:260000$Fihjg6ZGVBNb0gIi$d5519a24a6ebc1837620415026917e402b4562b05327645d772b7ffbe959776a');
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

-- Dump completed on 2024-02-05 18:06:13
