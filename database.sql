--
-- Table structure for table `Serverdata`
--

DROP TABLE IF EXISTS `Serverdata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Serverdata` (
  `IndexValue` varchar(32) NOT NULL,
  `HostName` varchar(255) DEFAULT NULL,
  `OS` varchar(255) DEFAULT NULL,
  `IP` varchar(255) DEFAULT NULL,
  `MAC` varchar(32) DEFAULT NULL,
  `CPU` varchar(255) DEFAULT NULL,
  `CPUCore` int DEFAULT NULL,
  `CPUCount` int DEFAULT NULL,
  `TotalCore` int DEFAULT NULL,
  `ThreadsPerCore` int DEFAULT NULL,
  `ThreadsTotal` int DEFAULT NULL,
  `Memory` varchar(255) DEFAULT NULL,
  `Vendor` varchar(255) DEFAULT NULL,
  `ProductName` varchar(255) DEFAULT NULL,
  `SerialNo` varchar(255) DEFAULT NULL,
  `Status` varchar(3) DEFAULT '0',
  `Update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Strike` tinyint DEFAULT '0',
  `BeforeHost` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`IndexValue`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
