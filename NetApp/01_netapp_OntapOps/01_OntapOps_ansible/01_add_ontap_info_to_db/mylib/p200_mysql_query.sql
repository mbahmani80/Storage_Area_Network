localhost ontapdb1> select * from t_customer;
+-------------+---------------+--------------------+------------------+
| customer_id | customer_name | customer_email     | customer_address |
+-------------+---------------+--------------------+------------------+
|           1 | Test_customer2      | Test_customer2@test.com  | test address     |
|           2 | Test_customer | tcustomer@test.com | Test address     |
|           3 | Test_customer3          |                    |                  |
+-------------+---------------+--------------------+------------------+
3 rows in set (0.001 sec)

-----------------------------------------------------------------------

To show all datacenter_name for a specific customer_name, you can use a JOIN query between the t_customer and t_datacenters tables. Here is an example query to achieve this:

SELECT `d`.`datacenter_name`
FROM `t_datacenters` AS `d`
JOIN `t_customer` AS `c` ON `d`.`customer_id` = `c`.`customer_id`
WHERE `c`.`customer_name` = 'Customer A';

localhost ontapdb1> SELECT `d`.`datacenter_name`
    -> FROM `t_datacenters` AS `d`
    -> JOIN `t_customer` AS `c` ON `d`.`customer_id` = `c`.`customer_id`
    -> WHERE `c`.`customer_name` = 'Test_customer3';
+-----------------+
| datacenter_name |
+-----------------+
| Bonn            |
| Berlin          |
+-----------------+
2 rows in set (0.001 sec)


-----------------------------------------------------------------------
To list all datacenter_id for a specific customer_name, you can use a similar JOIN query as before, but select the datacenter_id instead of the datacenter_name. Here is the query:

SELECT `d`.`datacenter_id`
FROM `t_datacenters` AS `d`
JOIN `t_customer` AS `c` ON `d`.`customer_id` = `c`.`customer_id`
WHERE `c`.`customer_name` = 'Customer A';


localhost ontapdb1> SELECT `d`.`datacenter_id` FROM `t_datacenters` AS `d` JOIN `t_customer` AS `c` ON `d`.`customer_id` = `c`.`customer_id` WHERE `c`.`customer_name` = 'Test_customer3';
+---------------+
| datacenter_id |
+---------------+
|             3 |
|             4 |
+---------------+
2 rows in set (0.001 sec)

localhost ontapdb1>

-----------------------------------------------------------------------
To show all stg_name from the t_stg_info table for a specific customer_name, you can use a JOIN query between the t_stg_info and t_customer tables. Here is the query:

SELECT `s`.`stg_name`
FROM `t_stg_info` AS `s`
JOIN `t_customer` AS `c` ON `s`.`customer_id` = `c`.`customer_id`
WHERE `c`.`customer_name` = 'Customer A';

localhost ontapdb1> SELECT `s`.`stg_name` FROM `t_stg_info` AS `s` JOIN `t_customer` AS `c` ON `s`.`customer_id` = `c`.`customer_id` WHERE `c`.`customer_name` = 'Test_customer3';
+----------+
| stg_name |
+----------+
| stg12   |
| stgbk12 |
| stgbk14 |
| stor-b   |
+----------+
4 rows in set (0.001 sec)

localhost ontapdb1>

-----------------------------------------------------------------------
To retrieve all columns (*) from the t_stg_info table for a specific datacenter_name, you'll need to join the t_stg_info, t_datacenters, and t_customer tables together. Here's how you can construct the query:

SELECT s.*
FROM t_stg_info s
JOIN t_datacenters d ON s.datacenter_id = d.datacenter_id
WHERE d.datacenter_name = $datacenter_name 
ORDER BY s.stg_name;


-----------------------------------------------------------------------
To retrieve the node_name, node_storage_config, and node_version from t_stg_node_info for a specific stg_name from t_stg_info, you can use a SQL query with a JOIN clause. Here’s an example query:

SELECT 
    tni.node_name, 
    tni.node_model,
    tni.node_location,
    tni.node_storage_configuration, 
    tni.node_version
FROM 
    t_stg_node_info tni
JOIN 
    t_stg_info tsi ON tni.stg_uuid = tsi.stg_uuid
WHERE 
    tsi.stg_name = '$stg_name';

localhost ontapdb1> SELECT
    ->     tni.node_name,
    ->     tni.node_model,
    ->     tni.node_location,
    ->     tni.node_storage_configuration,
    ->     tni.node_version
    -> FROM
    ->     t_stg_node_info tni
    -> JOIN
    ->     t_stg_info tsi ON tni.stg_uuid = tsi.stg_uuid
    -> WHERE
    ->     tsi.stg_name = 'stg12';
+-----------+------------+---------------+----------------------------+-------------------------------------------------------+
| node_name | node_model | node_location | node_storage_configuration | node_version                                          |
+-----------+------------+---------------+----------------------------+-------------------------------------------------------+
| n4-stg12 | AFF-C250   |               | single_path_ha             | NetApp Release 9.13.1P8: Fri Feb 23 14:13:29 UTC 2024 |
| n3-stg12 | AFF-C250   |               | single_path_ha             | NetApp Release 9.13.1P8: Fri Feb 23 14:13:29 UTC 2024 |
+-----------+------------+---------------+----------------------------+-------------------------------------------------------+
2 rows in set (0.001 sec)

localhost ontapdb1>

-----------------------------------------------------------------------
URL: 
http://172.28.30.16:3000/d/datacenter-list-dashboard/datacenter-list-dashboard?customer_id=$customer_id&datacenter_id=$datacenter_id&stg_uuid=$stg_uuid&customer_name=$customer_name"

"
-----------------------------------------------------------------------
SELECT vol_name, access_protocols, junction_path, vol_svm_name 
FROM t_volumes 
WHERE access_protocols LIKE '%iSCSI%' 
AND junction_path IS NULL;
-----------------------------------------------------------------------
select vol_name,access_protocols,junction_path,vol_svm_name from t_volumes where access_protocols like "%NFS%";
select vol_name,access_protocols,junction_path,vol_svm_name from t_volumes where access_protocols like "%CIFS%";
-----------------------------------------------------------------------

MariaDB [ontapdb1]> select vol_name,access_protocols,junction_path,vol_svm_name,vol_type,stg_name,activity_tracking_unsupported_reason,stg_name  from t_volumes where access_protocols  like "%iSCSI or FC LUN%" and junction_path like "%/%";
+---------------------+------------------+------------------------+---------------+----------+------------+-------------------------------------------------------------------------+------------+
| vol_name            | access_protocols | junction_path          | vol_svm_name  | vol_type | stg_name   | activity_tracking_unsupported_reason                                    | stg_name   |
+---------------------+------------------+------------------------+---------------+----------+------------+-------------------------------------------------------------------------+------------+
+---------------------+------------------+------------------------+---------------+----------+------------+-------------------------------------------------------------------------+------------+
15 rows in set (0,002 sec)

MariaDB [ontapdb1]>

Last login time: 9/9/2024 15:34:07
stg52st006::>  vol show stg5_vol1__cifs  -fields junction-path,activity-tracking-unsupported-reason,type,policy,snapshot-policy
vserver    volume                 policy  junction-path           type snapshot-policy              activity-tracking-unsupported-reason
---------- ---------------------- ------- ----------------------- ---- ---------------------------- ------------------------------------
stg52vs010 stg5_vol1__cifs default /stg5_vol1__cifs RW   stg52vs010_snap_14x3h_14d_5w -

stg52st006::> lun show -volume  cad_data_cifs
Vserver   Path                            State   Mapped   Type        Size
--------- ------------------------------- ------- -------- -------- --------
stg52vs010
          /vol/cad_data_cifs/cad_data/cad_data.lun
                                          online  unmapped windows   60.00GB

stg52st006::>

MariaDB [ontapdb1]> select vol_name,access_protocols,junction_path,vol_svm_name,vol_type,stg_name from t_volumes where junction_path  like "%/(%";


+-------------------------------------------+------------------+----------------------------------------------+-----------------------+----------+----------------+
213 rows in set (0,001 sec)



select vol_name,access_protocols,junction_path,vol_svm_name,vol_type,activity_tracking_unsupported_reason,stg_name,vol_nas_export_policy  from t_volumes where access_protocols  is NULL;
select * from t_svms ts;

MariaDB [ontapdb1]> select vol_name,access_protocols,junction_path,vol_svm_name,vol_type,activity_tracking_unsupported_reason,stg_name,vol_nas_export_policy  from t_volumes where access_protocols  is NULL;
+---------------------------------------------+------------------+----------------------------------------------+--------------+----------+--------------------------------------+------------+------------------------+
| vol_name                                    | access_protocols | junction_path                                | vol_svm_name | vol_type | activity_tracking_unsupported_reason | stg_name   | vol_nas_export_policy  |
+---------------------------------------------+------------------+----------------------------------------------+--------------+----------+--------------------------------------+------------+------------------------+
17 rows in set (0,002 sec)

MariaDB [ontapdb1]>


UPDATE t_volumes tv
JOIN t_svms ts ON tv.vol_svm_name = ts.svm_name
SET tv.access_protocols = 'mc_vol'
WHERE tv.access_protocols IS NULL
AND ts.svm_state = 'stopped'
AND ts.svm_subtype = 'sync_destination';



select vol_name,access_protocols,junction_path,vol_svm_name,vol_type,activity_tracking_unsupported_reason,stg_name  from t_volumes where access_protocols like "%mc_vol%";

MariaDB [ontapdb1]> select vol_name,access_protocols,junction_path,vol_svm_name,stg_name,vol_nas_export_policy  from t_volumes where access_protocols  is NULL;                 +---------------------------------------------+------------------+----------------------------------------------+--------------+------------+------------------------+
| vol_name                                    | access_protocols | junction_path                                | vol_svm_name | stg_name   | vol_nas_export_policy  |
+---------------------------------------------+------------------+----------------------------------------------+--------------+------------+------------------------+
+---------------------------------------------+------------------+----------------------------------------------+--------------+------------+------------------------+
17 rows in set (0,001 sec)

MariaDB [ontapdb1]>

UPDATE t_volumes
SET access_protocols = CASE
    WHEN vol_nas_export_policy != 'default' AND junction_path IS NOT NULL THEN 'NFS'
    WHEN vol_nas_export_policy = 'default' AND junction_path IS NULL THEN 'CIFS'
    ELSE access_protocols
END
WHERE access_protocols IS NULL;


MariaDB [ontapdb1]> UPDATE t_volumes
    -> SET access_protocols = CASE
    ->     WHEN vol_nas_export_policy != 'default' AND junction_path IS NOT NULL THEN 'NFS'
    ->     WHEN vol_nas_export_policy = 'default' AND junction_path IS NULL THEN 'CIFS'
    ->     ELSE access_protocols
    -> END
    -> WHERE access_protocols IS NULL;
Query OK, 15 rows affected (0,004 sec)
Rows matched: 17  Changed: 15  Warnings: 0

MariaDB [ontapdb1]> select vol_name,access_protocols,junction_path,vol_svm_name,stg_name,vol_nas_export_policy  from t_volumes where access_protocols  is NULL;
+---------------------------------------------+------------------+----------------------------------------------+--------------+------------+-----------------------+
| vol_name                                    | access_protocols | junction_path                                | vol_svm_name | stg_name   | vol_nas_export_policy |
+---------------------------------------------+------------------+----------------------------------------------+--------------+------------+-----------------------+
+---------------------------------------------+------------------+----------------------------------------------+--------------+------------+-----------------------+
2 rows in set (0,001 sec)

MariaDB [ontapdb1]>


MariaDB [ontapdb1]> select vol_name,access_protocols,junction_path,vol_svm_name,stg_name,vol_nas_export_policy  from t_volumes where access_protocols = "None";
+---------------------------------------------+------------------+----------------------------------------------+--------------+------------+-----------------------+
| vol_name                                    | access_protocols | junction_path                                | vol_svm_name | stg_name   | vol_nas_export_policy |

MariaDB [ontapdb1]>

