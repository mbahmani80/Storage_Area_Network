-- MariaDB dump 10.19  Distrib 10.6.16-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: ontapdb1
-- ------------------------------------------------------
-- Server version	10.6.16-MariaDB-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `t_aggregates`
--

DROP TABLE IF EXISTS `t_aggregates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_aggregates` (
  `aggr_name` varchar(255) DEFAULT NULL,
  `aggr_uuid` varchar(255) NOT NULL,
  `aggr_state` varchar(50) DEFAULT NULL,
  `aggr_available_space` int(11) DEFAULT NULL,
  `aggr_total_size` int(11) DEFAULT NULL,
  `aggr_used_space` int(11) DEFAULT NULL,
  `aggr_storage_type` varchar(50) DEFAULT NULL,
  `aggr_vol_count` int(11) DEFAULT NULL,
  `aggr_node_name` varchar(255) DEFAULT NULL,
  `aggr_node_uuid` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`aggr_uuid`),
  KEY `aggr_node_uuid` (`aggr_node_uuid`),
  CONSTRAINT `t_aggregates_ibfk_1` FOREIGN KEY (`aggr_node_uuid`) REFERENCES `t_ontap_node_info` (`node_uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_customer`
--

DROP TABLE IF EXISTS `t_customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_customer` (
  `customer_id` int(11) NOT NULL AUTO_INCREMENT,
  `customer_name` varchar(255) DEFAULT NULL,
  `customer_email` varchar(255) DEFAULT NULL,
  `customer_address` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`customer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_datacenters`
--

DROP TABLE IF EXISTS `t_datacenters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_datacenters` (
  `datacenter_id` int(11) NOT NULL AUTO_INCREMENT,
  `datacenter_name` varchar(255) DEFAULT NULL,
  `datacenter_location` varchar(255) DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`datacenter_id`),
  KEY `customer_id` (`customer_id`),
  CONSTRAINT `t_datacenters_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `t_customer` (`customer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_ontap_info`
--

DROP TABLE IF EXISTS `t_ontap_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_ontap_info` (
  `stg_name` varchar(255) DEFAULT NULL,
  `stg_uuid` varchar(255) NOT NULL,
  `stg_version` varchar(255) DEFAULT NULL,
  `stg_mgmt_ip` varchar(255) DEFAULT NULL,
  `stg_timezone` text DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `datacenter_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`stg_uuid`),
  KEY `customer_id` (`customer_id`),
  KEY `datacenter_id` (`datacenter_id`),
  CONSTRAINT `t_ontap_info_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `t_customer` (`customer_id`),
  CONSTRAINT `t_ontap_info_ibfk_2` FOREIGN KEY (`datacenter_id`) REFERENCES `t_datacenters` (`datacenter_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_ontap_node_info`
--

DROP TABLE IF EXISTS `t_ontap_node_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_ontap_node_info` (
  `node_name` varchar(255) DEFAULT NULL,
  `node_uuid` varchar(255) NOT NULL,
  `node_model` varchar(255) DEFAULT NULL,
  `node_serial_number` varchar(255) DEFAULT NULL,
  `node_system_id` varchar(255) DEFAULT NULL,
  `node_storage_configuration` text DEFAULT NULL,
  `node_location` varchar(255) DEFAULT NULL,
  `node_version` varchar(50) DEFAULT NULL,
  `stg_uuid` varchar(255) DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `datacenter_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`node_uuid`),
  KEY `customer_id` (`customer_id`),
  KEY `datacenter_id` (`datacenter_id`),
  KEY `stg_uuid` (`stg_uuid`),
  CONSTRAINT `t_ontap_node_info_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `t_customer` (`customer_id`),
  CONSTRAINT `t_ontap_node_info_ibfk_2` FOREIGN KEY (`datacenter_id`) REFERENCES `t_datacenters` (`datacenter_id`),
  CONSTRAINT `t_ontap_node_info_ibfk_3` FOREIGN KEY (`stg_uuid`) REFERENCES `t_ontap_info` (`stg_uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_svms`
--

DROP TABLE IF EXISTS `t_svms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_svms` (
  `svm_name` varchar(255) DEFAULT NULL,
  `svm_uuid` varchar(255) NOT NULL,
  `svm_language` varchar(50) DEFAULT NULL,
  `svm_state` varchar(50) DEFAULT NULL,
  `svm_subtype` varchar(50) DEFAULT NULL,
  `svm_comment` text DEFAULT NULL,
  `svm_aggregates_name` varchar(255) DEFAULT NULL,
  `svm_aggregates_uuid` varchar(255) DEFAULT NULL,
  `svm_ip_address` varchar(50) DEFAULT NULL,
  `svm_ip_name` varchar(50) DEFAULT NULL,
  `svm_cifs_allowed` tinyint(1) DEFAULT NULL,
  `svm_cifs_enabled` tinyint(1) DEFAULT NULL,
  `svm_fcp_allowed` tinyint(1) DEFAULT NULL,
  `svm_fcp_enabled` tinyint(1) DEFAULT NULL,
  `svm_iscsi_allowed` tinyint(1) DEFAULT NULL,
  `svm_iscsi_enabled` tinyint(1) DEFAULT NULL,
  `svm_nfs_allowed` tinyint(1) DEFAULT NULL,
  `svm_nfs_enabled` tinyint(1) DEFAULT NULL,
  `svm_s3_allowed` tinyint(1) DEFAULT NULL,
  `svm_s3_enabled` tinyint(1) DEFAULT NULL,
  `svm_nvme_allowed` tinyint(1) DEFAULT NULL,
  `svm_nvme_enabled` tinyint(1) DEFAULT NULL,
  `svm_snapshot_policy` varchar(255) DEFAULT NULL,
  `svm_ipspace_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`svm_uuid`),
  KEY `svm_aggregates_uuid` (`svm_aggregates_uuid`),
  CONSTRAINT `t_svms_ibfk_1` FOREIGN KEY (`svm_aggregates_uuid`) REFERENCES `t_aggregates` (`aggr_uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_volumes`
--

DROP TABLE IF EXISTS `t_volumes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_volumes` (
  `vol_name` varchar(255) DEFAULT NULL,
  `vol_uuid` varchar(255) NOT NULL,
  `vol_state` varchar(50) DEFAULT NULL,
  `vol_type` varchar(50) DEFAULT NULL,
  `vol_style` varchar(50) DEFAULT NULL,
  `vol_size` int(11) DEFAULT NULL,
  `vol_comment` text DEFAULT NULL,
  `vol_creation_time` datetime DEFAULT NULL,
  `vol_language` varchar(50) DEFAULT NULL,
  `vol_snapshot_policy` varchar(255) DEFAULT NULL,
  `vol_nas_export_policy` varchar(255) DEFAULT NULL,
  `vol_svm_name` varchar(255) DEFAULT NULL,
  `vol_svm_uuid` varchar(255) DEFAULT NULL,
  `vol_is_flexclone` varchar(255) DEFAULT NULL,
  `vol_snapmirror_protected` varchar(255) DEFAULT NULL,
  `vol_ggregates_name` varchar(255) DEFAULT NULL,
  `vol_aggregates_uuid` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`vol_uuid`),
  KEY `vol_svm_uuid` (`vol_svm_uuid`),
  KEY `vol_aggregates_uuid` (`vol_aggregates_uuid`),
  CONSTRAINT `t_volumes_ibfk_1` FOREIGN KEY (`vol_svm_uuid`) REFERENCES `t_svms` (`svm_uuid`),
  CONSTRAINT `t_volumes_ibfk_2` FOREIGN KEY (`vol_aggregates_uuid`) REFERENCES `t_aggregates` (`aggr_uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-04-30 12:17:15
