/*
 Navicat Premium Data Transfer

 Source Server         : coc
 Source Server Type    : MySQL
 Source Server Version : 50733
 Source Host           : 127.0.0.1:3306
 Source Schema         : claudecn

 Target Server Type    : MySQL
 Target Server Version : 50733
 File Encoding         : 65001

 Date: 24/12/2023 19:14:08
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for t_captcha
-- ----------------------------
DROP TABLE IF EXISTS `t_captcha`;
CREATE TABLE `t_captcha`  (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `captcha_text` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 657 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for t_conversation
-- ----------------------------
DROP TABLE IF EXISTS `t_conversation`;
CREATE TABLE `t_conversation`  (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `member_id` int(11) NOT NULL,
  `session_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `content_in` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `content_out` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `del_flag` bit(1) NOT NULL DEFAULT b'0',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_member_id`(`member_id`) USING BTREE,
  INDEX `idx_session_id`(`session_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 41 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for t_member
-- ----------------------------
DROP TABLE IF EXISTS `t_member`;
CREATE TABLE `t_member`  (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `login_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '登录名',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '密码',
  `mobile` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '手机',
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '邮箱',
  `vip_level` tinyint(4) NULL DEFAULT NULL COMMENT '账号等级',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_login_time` timestamp NULL DEFAULT NULL COMMENT '最后登录时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
