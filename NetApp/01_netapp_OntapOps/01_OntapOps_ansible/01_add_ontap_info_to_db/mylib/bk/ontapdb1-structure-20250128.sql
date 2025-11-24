/*!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.6.18-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: ontapdb1
-- ------------------------------------------------------
-- Server version	10.6.18-MariaDB-0ubuntu0.22.04.1

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
  `aggr_available_space` bigint(20) DEFAULT NULL,
  `aggr_total_size` bigint(20) DEFAULT NULL,
  `aggr_used_space` bigint(20) DEFAULT NULL,
  `aggr_storage_type` varchar(50) DEFAULT NULL,
  `aggr_vol_count` int(11) DEFAULT NULL,
  `aggr_node_name` varchar(255) DEFAULT NULL,
  `aggr_node_uuid` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`aggr_uuid`),
  KEY `aggregates_ibfk_1` (`aggr_node_uuid`),
  CONSTRAINT `aggregates_ibfk_1` FOREIGN KEY (`aggr_node_uuid`) REFERENCES `t_stg_node_info` (`node_uuid`) ON DELETE CASCADE,
  CONSTRAINT `t_aggregates_ibfk_1` FOREIGN KEY (`aggr_node_uuid`) REFERENCES `t_stg_node_info` (`node_uuid`)
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
  `customer_name` varchar(255) NOT NULL,
  `customer_email` varchar(255) DEFAULT NULL,
  `customer_address` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`customer_id`),
  UNIQUE KEY `customer_id` (`customer_id`),
  UNIQUE KEY `customer_name` (`customer_name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
  `datacenter_country` char(2) DEFAULT NULL,
  `datacenter_city` varchar(255) DEFAULT NULL,
  `datacenter_address` varchar(255) DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`datacenter_id`),
  KEY `customer_id` (`customer_id`),
  CONSTRAINT `datacenters_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `t_customer` (`customer_id`) ON DELETE CASCADE,
  CONSTRAINT `t_datacenters_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `t_customer` (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_lun_mapping`
--

DROP TABLE IF EXISTS `t_lun_mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_lun_mapping` (
  `lun_igroup` text NOT NULL,
  `vserver` varchar(255) DEFAULT NULL,
  `path` text DEFAULT NULL,
  `volume` varchar(255) DEFAULT NULL,
  `lun` varchar(255) DEFAULT NULL,
  `igroup` varchar(255) DEFAULT NULL,
  `ostype` varchar(255) DEFAULT NULL,
  `protocol` varchar(255) DEFAULT NULL,
  `lun_id` int(11) DEFAULT NULL,
  `initiators` text DEFAULT NULL,
  `stg_name` varchar(255) DEFAULT NULL,
  UNIQUE KEY `unique_lun_initiators` (`lun_igroup`) USING HASH
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_snapmirror_info`
--

DROP TABLE IF EXISTS `t_snapmirror_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_snapmirror_info` (
  `backup_stg_name` varchar(255) DEFAULT NULL,
  `customer_id` varchar(255) DEFAULT NULL,
  `source_path` varchar(255) DEFAULT NULL,
  `source_vserver` varchar(255) DEFAULT NULL,
  `source_volume` varchar(255) DEFAULT NULL,
  `destination_path` varchar(255) DEFAULT NULL,
  `destination_vserver` varchar(255) DEFAULT NULL,
  `destination_volume` varchar(255) DEFAULT NULL,
  `policy` varchar(255) DEFAULT NULL,
  `lag_time` varchar(255) DEFAULT NULL,
  `source_path_destination_path` varchar(255) NOT NULL,
  PRIMARY KEY (`source_path_destination_path`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_snapshots`
--

DROP TABLE IF EXISTS `t_snapshots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_snapshots` (
  `snapshot_name` varchar(255) DEFAULT NULL,
  `snapshot_comment` varchar(255) DEFAULT NULL,
  `vol_name` varchar(255) DEFAULT NULL,
  `stg_name` varchar(255) DEFAULT NULL,
  `svm_name` varchar(255) DEFAULT NULL,
  `snapshot_create_time` varchar(255) DEFAULT NULL,
  `snapmirror_label` varchar(255) DEFAULT NULL,
  `stg_uuid_vserver_snap_create_time` varchar(255) NOT NULL,
  KEY `snapshots_ibfk_1` (`stg_name`),
  CONSTRAINT `snapshots_ibfk_1` FOREIGN KEY (`stg_name`) REFERENCES `t_stg_info` (`stg_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_stg_access_data`
--

DROP TABLE IF EXISTS `t_stg_access_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_stg_access_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `storageip` varchar(15) DEFAULT NULL,
  `storagename` varchar(255) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  `password` text DEFAULT NULL,
  `https` tinyint(1) DEFAULT NULL,
  `validate_certs` tinyint(1) DEFAULT NULL,
  `configtype` varchar(255) DEFAULT NULL,
  `enabled` tinyint(1) DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_storage` (`storageip`,`storagename`),
  KEY `fk_customer` (`customer_id`),
  CONSTRAINT `fk_customer` FOREIGN KEY (`customer_id`) REFERENCES `t_customer` (`customer_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_stg_info`
--

DROP TABLE IF EXISTS `t_stg_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_stg_info` (
  `stg_name` varchar(255) DEFAULT NULL,
  `stg_uuid` varchar(255) NOT NULL,
  `stg_version` varchar(255) DEFAULT NULL,
  `stg_mgmt_ip` varchar(255) DEFAULT NULL,
  `stg_timezone` text DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `datacenter_id` int(11) DEFAULT NULL,
  `metrocluster_local_configuration_state` varchar(255) DEFAULT NULL,
  `metrocluster_remote_cluster_name` varchar(255) DEFAULT NULL,
  `metrocluster_remote_cluster_uuid` varchar(255) DEFAULT NULL,
  `metrocluster_remote_configuration_state` varchar(255) DEFAULT NULL,
  `metrocluster_configuration_type` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`stg_uuid`),
  KEY `stg_info_ibfk_1` (`customer_id`),
  KEY `stg_info_ibfk_2` (`datacenter_id`),
  KEY `idx_stg_name` (`stg_name`),
  CONSTRAINT `stg_info_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `t_customer` (`customer_id`) ON DELETE CASCADE,
  CONSTRAINT `stg_info_ibfk_2` FOREIGN KEY (`datacenter_id`) REFERENCES `t_datacenters` (`datacenter_id`) ON DELETE CASCADE,
  CONSTRAINT `t_stg_info_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `t_customer` (`customer_id`),
  CONSTRAINT `t_stg_info_ibfk_2` FOREIGN KEY (`datacenter_id`) REFERENCES `t_datacenters` (`datacenter_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_stg_node_info`
--

DROP TABLE IF EXISTS `t_stg_node_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_stg_node_info` (
  `node_name` varchar(255) DEFAULT NULL,
  `node_uuid` varchar(255) NOT NULL,
  `node_model` varchar(255) DEFAULT NULL,
  `node_serial_number` varchar(255) DEFAULT NULL,
  `node_system_id` varchar(255) DEFAULT NULL,
  `node_storage_configuration` text DEFAULT NULL,
  `node_location` varchar(255) DEFAULT NULL,
  `node_version` varchar(255) DEFAULT NULL,
  `stg_uuid` varchar(255) DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `datacenter_id` int(11) DEFAULT NULL,
  `node_mgmt_lif` varchar(255) DEFAULT NULL,
  `node_service_processor` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`node_uuid`),
  KEY `stg_node_info_ibfk_1` (`customer_id`),
  KEY `stg_node_info_ibfk_2` (`datacenter_id`),
  KEY `stg_node_info_ibfk_3` (`stg_uuid`),
  CONSTRAINT `stg_node_info_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `t_customer` (`customer_id`) ON DELETE CASCADE,
  CONSTRAINT `stg_node_info_ibfk_2` FOREIGN KEY (`datacenter_id`) REFERENCES `t_datacenters` (`datacenter_id`) ON DELETE CASCADE,
  CONSTRAINT `stg_node_info_ibfk_3` FOREIGN KEY (`stg_uuid`) REFERENCES `t_stg_info` (`stg_uuid`) ON DELETE CASCADE,
  CONSTRAINT `t_stg_node_info_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `t_customer` (`customer_id`),
  CONSTRAINT `t_stg_node_info_ibfk_2` FOREIGN KEY (`datacenter_id`) REFERENCES `t_datacenters` (`datacenter_id`),
  CONSTRAINT `t_stg_node_info_ibfk_3` FOREIGN KEY (`stg_uuid`) REFERENCES `t_stg_info` (`stg_uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_stg_peer_info`
--

DROP TABLE IF EXISTS `t_stg_peer_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_stg_peer_info` (
  `stg_name` varchar(255) DEFAULT NULL,
  `stg_uuid` varchar(255) DEFAULT NULL,
  `stg_peer_name` varchar(255) DEFAULT NULL,
  `stg_peer_uuid` varchar(255) DEFAULT NULL,
  `stg_peer_status_state` varchar(255) DEFAULT NULL,
  `stg_peer_remote_name` varchar(255) DEFAULT NULL,
  `stg_peer_remote_serial_number` varchar(255) DEFAULT NULL,
  `stg_peer_remote_ip_addresses` varchar(255) DEFAULT NULL,
  `stg_peer_applications` varchar(255) DEFAULT NULL,
  `stg_uuid_peer_uuid` varchar(255) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`stg_uuid_peer_uuid`),
  KEY `stg_peer_info_ibfk_1` (`stg_uuid`),
  KEY `fk_customer_id` (`customer_id`),
  CONSTRAINT `fk_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `t_customer` (`customer_id`),
  CONSTRAINT `stg_peer_info_ibfk_1` FOREIGN KEY (`stg_uuid`) REFERENCES `t_stg_info` (`stg_uuid`) ON DELETE CASCADE,
  CONSTRAINT `t_stg_peer_info_ibfk_1` FOREIGN KEY (`stg_uuid`) REFERENCES `t_stg_info` (`stg_uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_svm_peer_info`
--

DROP TABLE IF EXISTS `t_svm_peer_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_svm_peer_info` (
  `stg_name` varchar(255) DEFAULT NULL,
  `stg_uuid` varchar(255) DEFAULT NULL,
  `peer_uuid` varchar(255) DEFAULT NULL,
  `peer_name` varchar(255) DEFAULT NULL,
  `svm_name` varchar(255) DEFAULT NULL,
  `svm_uuid` varchar(255) DEFAULT NULL,
  `peer_state` varchar(255) DEFAULT NULL,
  `peer_svm_name` varchar(255) DEFAULT NULL,
  `peer_svm_uuid` varchar(255) DEFAULT NULL,
  `peer_cluster_name` varchar(255) DEFAULT NULL,
  `peer_cluster_uuid` varchar(255) DEFAULT NULL,
  `applications` varchar(255) DEFAULT NULL,
  `stg_uuid_peer_uuid` varchar(255) NOT NULL,
  PRIMARY KEY (`stg_uuid_peer_uuid`)
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
  `stg_name` varchar(255) NOT NULL,
  `stg_uuid_svm_uuid` varchar(255) NOT NULL,
  `stg_uuid` varchar(255) NOT NULL,
  PRIMARY KEY (`stg_uuid_svm_uuid`),
  UNIQUE KEY `stg_uuid_svm_uuid` (`stg_uuid_svm_uuid`),
  KEY `fk_svms_stg_uuid` (`stg_uuid`),
  CONSTRAINT `fk_svms_stg_uuid` FOREIGN KEY (`stg_uuid`) REFERENCES `t_stg_info` (`stg_uuid`) ON DELETE CASCADE
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
  `vol_size` bigint(20) DEFAULT NULL,
  `vol_comment` text DEFAULT NULL,
  `vol_creation_time` varchar(100) DEFAULT NULL,
  `vol_language` varchar(50) DEFAULT NULL,
  `vol_snapshot_policy` varchar(255) DEFAULT NULL,
  `vol_nas_export_policy` varchar(255) DEFAULT NULL,
  `vol_svm_name` varchar(255) DEFAULT NULL,
  `vol_svm_uuid` varchar(255) DEFAULT NULL,
  `vol_is_flexclone` varchar(255) DEFAULT NULL,
  `vol_snapmirror_protected` varchar(255) DEFAULT NULL,
  `vol_aggregates_name` varchar(255) DEFAULT NULL,
  `vol_aggregates_uuid` varchar(255) DEFAULT NULL,
  `stg_uuid_vol_uuid` varchar(255) NOT NULL,
  `stg_name` varchar(255) NOT NULL,
  `access_protocols` varchar(255) DEFAULT NULL,
  `junction_path` varchar(255) DEFAULT NULL,
  `activity_tracking_unsupported_reason` text DEFAULT NULL,
  `snapshot_count` int(11) DEFAULT 0,
  PRIMARY KEY (`stg_uuid_vol_uuid`)
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

-- Dump completed on 2025-01-28 13:00:30
