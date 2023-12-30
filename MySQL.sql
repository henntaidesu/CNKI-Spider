CREATE TABLE `cnki_index` (
  `UUID` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `title` varchar(700) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `receive_time` datetime DEFAULT NULL,
  `from` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`title`),
  KEY `from` (`from`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `cnki_paper_information` (
  `UUID` char(36) NOT NULL,
  `institute` varchar(512) DEFAULT NULL,
  `paper_from` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `db_type` varchar(12) DEFAULT NULL,
  `down_sun` int DEFAULT NULL,
  `quote` int DEFAULT NULL,
  `insert_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `funding` varchar(700) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `album` varchar(255) DEFAULT NULL,
  `classification_number` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `article_directory` text,
  `Topics` varchar(255) DEFAULT NULL,
  `level` varchar(12) DEFAULT NULL,
  `page_sum` int DEFAULT NULL,
  `journal` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '期刊',
  `master` text COMMENT '硕士论文',
  `PhD` text COMMENT '博士',
  `international_journals` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '国际期刊',
  `book` text COMMENT '图书',
  `Chinese_and_foreign` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '中外文题录',
  `newpaper` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '报纸',
  PRIMARY KEY (`UUID`),
  KEY `db` (`db_type`),
  KEY `level` (`level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `index` (
  `UUID` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `web_site_id` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `classification_en` varchar(700) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `classification_zh` varchar(700) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `source_language` char(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `title_zh` varchar(700) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `title_en` varchar(700) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `update_time` datetime(3) DEFAULT NULL,
  `insert_time` datetime(3) DEFAULT NULL,
  `from` varchar(256) DEFAULT NULL,
  `state` char(2) DEFAULT NULL,
  `authors` varchar(512) DEFAULT NULL,
  `Introduction` varchar(9182) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `receive_time` datetime DEFAULT NULL,
  `Journal_reference` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `Comments` varchar(2048) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `size` double DEFAULT NULL,
  `DOI` varchar(255) DEFAULT NULL,
  `version` char(1) DEFAULT NULL,
  `withdrawn` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`web_site_id`) USING BTREE,
  KEY `title_zh` (`title_zh`),
  KEY `title_en` (`title_en`),
  KEY `index` (`UUID`,`web_site_id`) USING BTREE,
  KEY `classification_en` (`classification_en`),
  KEY `classification_cn` (`classification_zh`),
  KEY `state` (`state`),
  KEY `receive_time` (`receive_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;