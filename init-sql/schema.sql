-- Adminer 5.4.1 MySQL 8.0.44 dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

SET NAMES utf8mb4;

DROP DATABASE IF EXISTS `rms`;
CREATE DATABASE `rms` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `rms`;

DROP TABLE IF EXISTS `bills`;
CREATE TABLE `bills` (
  `id` int NOT NULL AUTO_INCREMENT,
  `total_amount` decimal(10,2) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` int NOT NULL,
  `order_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `bills_created_by_id_0dacd544_fk_users_id` (`created_by_id`),
  KEY `bills_order_id_a6e91d98_fk_orders_id` (`order_id`),
  CONSTRAINT `bills_created_by_id_0dacd544_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `bills_order_id_a6e91d98_fk_orders_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `combo_dishes`;
CREATE TABLE `combo_dishes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `quantity` int NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `deleted_at` datetime(6) DEFAULT NULL,
  `combo_id` int NOT NULL,
  `dish_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `combo_dishes_combo_id_64c83254_fk_combos_id` (`combo_id`),
  KEY `combo_dishes_dish_id_de1f8458_fk_dishes_id` (`dish_id`),
  CONSTRAINT `combo_dishes_combo_id_64c83254_fk_combos_id` FOREIGN KEY (`combo_id`) REFERENCES `combos` (`id`),
  CONSTRAINT `combo_dishes_dish_id_de1f8458_fk_dishes_id` FOREIGN KEY (`dish_id`) REFERENCES `dishes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `combos`;
CREATE TABLE `combos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `image` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `discount` int NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `deleted_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `dining_tables`;
CREATE TABLE `dining_tables` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `number_of_seats` int NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `deleted_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `dishes`;
CREATE TABLE `dishes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `image` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `deleted_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `order_items`;
CREATE TABLE `order_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `quantity` int NOT NULL,
  `note` longtext COLLATE utf8mb4_unicode_ci,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `deleted_at` datetime(6) DEFAULT NULL,
  `combo_id` int DEFAULT NULL,
  `dish_id` int DEFAULT NULL,
  `order_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `order_items_combo_id_985acbce_fk_combos_id` (`combo_id`),
  KEY `order_items_dish_id_13ed92e2_fk_dishes_id` (`dish_id`),
  KEY `order_items_order_id_412ad78b_fk_orders_id` (`order_id`),
  CONSTRAINT `order_items_combo_id_985acbce_fk_combos_id` FOREIGN KEY (`combo_id`) REFERENCES `combos` (`id`),
  CONSTRAINT `order_items_dish_id_13ed92e2_fk_dishes_id` FOREIGN KEY (`dish_id`) REFERENCES `dishes` (`id`),
  CONSTRAINT `order_items_order_id_412ad78b_fk_orders_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `orders`;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `customer_phone` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `finished_at` datetime(6) DEFAULT NULL,
  `note` longtext COLLATE utf8mb4_unicode_ci,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `dining_table_id` int NOT NULL,
  `employee_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `orders_dining_table_id_af4278e6_fk_dining_tables_id` (`dining_table_id`),
  KEY `orders_employee_id_098e8632_fk_users_id` (`employee_id`),
  CONSTRAINT `orders_dining_table_id_af4278e6_fk_dining_tables_id` FOREIGN KEY (`dining_table_id`) REFERENCES `dining_tables` (`id`),
  CONSTRAINT `orders_employee_id_098e8632_fk_users_id` FOREIGN KEY (`employee_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `employee_code` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fullname` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `birth_date` date DEFAULT NULL,
  `gender` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `employee_code` (`employee_code`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `users` (`password`, `last_login`, `id`, `employee_code`, `fullname`, `birth_date`, `gender`, `email`, `phone`, `status`, `role`, `created_at`, `updated_at`) VALUES
('pbkdf2_sha256$1000000$0x4S2TbXJHwWX0E6HQSJ6M$c1HZOXje0J4WzFJqPhyL9qvwlEgssatiGfJXQ+O6xmw=',	NULL,	1,	'NV00001',	'Quản lý',	'2025-11-12',	'male',	'manager@rms.com',	'string',	'activated',	'manager',	'2025-11-12 14:46:08.573944',	'2025-11-12 14:46:08.574784');

-- 2025-11-12 14:48:15 UTC