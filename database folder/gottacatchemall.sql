-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 29, 2025 at 08:26 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `gottacatchemall`
--

-- --------------------------------------------------------

--
-- Table structure for table `auction`
--

CREATE TABLE `auction` (
  `auction_id` int(11) NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `starting_bid` decimal(10,2) NOT NULL,
  `user_id` int(11) NOT NULL,
  `card_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `battle`
--

CREATE TABLE `battle` (
  `battle_id` int(11) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `date` datetime DEFAULT current_timestamp(),
  `winner` int(11) DEFAULT NULL,
  `loser` int(11) DEFAULT NULL,
  `status` enum('queued','ongoing','finished') DEFAULT 'queued'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `battle`
--

INSERT INTO `battle` (`battle_id`, `amount`, `date`, `winner`, `loser`, `status`) VALUES
(1, 50.00, '2025-08-25 10:00:00', 1, 2, 'queued'),
(2, 30.00, '2025-08-26 14:30:00', 3, 4, 'queued'),
(3, 40.00, '2025-08-27 16:45:00', 2, 1, 'queued'),
(4, 25.00, '2025-08-28 12:20:00', 7, 8, 'queued'),
(5, 60.00, '2025-08-28 18:10:00', 9, 10, 'queued'),
(6, 35.00, '2025-08-29 09:15:00', 4, 3, 'queued'),
(7, 20.00, '2025-08-29 11:50:00', 1, 3, 'queued'),
(8, 45.00, '2025-08-29 13:05:00', 8, 7, 'queued'),
(9, 55.00, '2025-08-29 15:40:00', 10, 9, 'queued'),
(10, 70.00, '2025-08-29 17:30:00', 2, 4, 'queued');

-- --------------------------------------------------------

--
-- Table structure for table `bids_in`
--

CREATE TABLE `bids_in` (
  `user_id` int(11) NOT NULL,
  `auction_id` int(11) NOT NULL,
  `bid_amount` decimal(10,2) NOT NULL,
  `timestamp` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `card`
--

CREATE TABLE `card` (
  `card_id` int(11) NOT NULL,
  `type` varchar(50) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `value` decimal(10,2) DEFAULT NULL,
  `normal` tinyint(1) DEFAULT NULL,
  `golden` tinyint(1) DEFAULT NULL,
  `holographic` tinyint(1) DEFAULT NULL,
  `owner_id` int(11) DEFAULT NULL,
  `trade_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `challenge`
--

CREATE TABLE `challenge` (
  `battle_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `card_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `notify`
--

CREATE TABLE `notify` (
  `user_id` int(11) NOT NULL,
  `auction_id` int(11) NOT NULL,
  `wishlist_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `participates_in`
--

CREATE TABLE `participates_in` (
  `trade_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `reward`
--

CREATE TABLE `reward` (
  `reward_id` int(11) NOT NULL,
  `value` decimal(10,2) NOT NULL,
  `Card` int(11) DEFAULT NULL,
  `Token` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `trade`
--

CREATE TABLE `trade` (
  `trade_id` int(11) NOT NULL,
  `date` datetime NOT NULL,
  `status` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `balance` decimal(10,2) DEFAULT 0.00,
  `join_date` date DEFAULT curdate(),
  `chatuser_id` int(11) DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `last_login` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `name`, `email`, `password`, `balance`, `join_date`, `chatuser_id`, `timestamp`, `last_login`) VALUES
(1, 'Maria', 'maria@example.com', 'a_very_secure_password', 0.00, '2025-08-19', NULL, '2025-08-18 19:35:22', NULL),
(2, 'John Doe', 'john.d@example.com', 'password123', 150.00, '2025-08-19', NULL, '2025-08-29 08:21:41', '2025-08-29'),
(3, 'Jane Smith', 'jane.s@example.com', 'another_pass', 125.50, '2025-08-19', NULL, '2025-08-29 15:55:08', '2025-08-29'),
(4, 'Peter Jones', 'p.jones@example.com', 'best_pass_ever', 100.00, '2025-08-19', NULL, '2025-08-18 19:41:38', NULL),
(7, 'alu', 'alu@gmail.com', 'helloalu', 100.00, '2025-08-29', NULL, '2025-08-29 08:19:17', '2025-08-29'),
(8, 'maomao', 'mao@gmail.com', 'alumao', 100.00, '2025-08-29', NULL, '2025-08-29 15:53:40', '2025-08-29'),
(9, 'saihan', 'saihan@gmail.com', 'saihanposa', 100.00, '2025-08-29', NULL, '2025-08-29 16:22:36', '2025-08-29'),
(10, 'mehu', 'mehu@gmail.com', 'mehu', 100.00, '2025-08-29', NULL, '2025-08-29 17:34:37', '2025-08-29');

-- --------------------------------------------------------

--
-- Table structure for table `wins`
--

CREATE TABLE `wins` (
  `user_id` int(11) NOT NULL,
  `reward_id` int(11) NOT NULL,
  `battle_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `wishlist`
--

CREATE TABLE `wishlist` (
  `wishlist_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `card_id` int(11) NOT NULL,
  `date_created` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `auction`
--
ALTER TABLE `auction`
  ADD PRIMARY KEY (`auction_id`),
  ADD KEY `fk_auction_user` (`user_id`),
  ADD KEY `fk_auction_card` (`card_id`);

--
-- Indexes for table `battle`
--
ALTER TABLE `battle`
  ADD PRIMARY KEY (`battle_id`);

--
-- Indexes for table `bids_in`
--
ALTER TABLE `bids_in`
  ADD PRIMARY KEY (`user_id`,`auction_id`),
  ADD KEY `auction_id` (`auction_id`);

--
-- Indexes for table `card`
--
ALTER TABLE `card`
  ADD PRIMARY KEY (`card_id`),
  ADD KEY `fk_owner` (`owner_id`),
  ADD KEY `fk_trade` (`trade_id`);

--
-- Indexes for table `challenge`
--
ALTER TABLE `challenge`
  ADD PRIMARY KEY (`battle_id`,`user_id`),
  ADD KEY `fk_challenge_user` (`user_id`),
  ADD KEY `fk_challenge_card` (`card_id`);

--
-- Indexes for table `notify`
--
ALTER TABLE `notify`
  ADD PRIMARY KEY (`user_id`,`auction_id`,`wishlist_id`),
  ADD KEY `auction_id` (`auction_id`),
  ADD KEY `wishlist_id` (`wishlist_id`);

--
-- Indexes for table `participates_in`
--
ALTER TABLE `participates_in`
  ADD PRIMARY KEY (`trade_id`,`user_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `reward`
--
ALTER TABLE `reward`
  ADD PRIMARY KEY (`reward_id`),
  ADD KEY `Card` (`Card`);

--
-- Indexes for table `trade`
--
ALTER TABLE `trade`
  ADD PRIMARY KEY (`trade_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `fk_chatuser` (`chatuser_id`);

--
-- Indexes for table `wins`
--
ALTER TABLE `wins`
  ADD PRIMARY KEY (`user_id`,`reward_id`,`battle_id`),
  ADD KEY `reward_id` (`reward_id`),
  ADD KEY `battle_id` (`battle_id`);

--
-- Indexes for table `wishlist`
--
ALTER TABLE `wishlist`
  ADD PRIMARY KEY (`wishlist_id`),
  ADD UNIQUE KEY `user_id` (`user_id`,`card_id`),
  ADD KEY `card_id` (`card_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `auction`
--
ALTER TABLE `auction`
  MODIFY `auction_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `battle`
--
ALTER TABLE `battle`
  MODIFY `battle_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `reward`
--
ALTER TABLE `reward`
  MODIFY `reward_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `trade`
--
ALTER TABLE `trade`
  MODIFY `trade_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `wishlist`
--
ALTER TABLE `wishlist`
  MODIFY `wishlist_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `auction`
--
ALTER TABLE `auction`
  ADD CONSTRAINT `fk_auction_card` FOREIGN KEY (`card_id`) REFERENCES `card` (`card_id`),
  ADD CONSTRAINT `fk_auction_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `bids_in`
--
ALTER TABLE `bids_in`
  ADD CONSTRAINT `bids_in_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `bids_in_ibfk_2` FOREIGN KEY (`auction_id`) REFERENCES `auction` (`auction_id`);

--
-- Constraints for table `card`
--
ALTER TABLE `card`
  ADD CONSTRAINT `fk_owner` FOREIGN KEY (`owner_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `fk_trade` FOREIGN KEY (`trade_id`) REFERENCES `trade` (`trade_id`);

--
-- Constraints for table `challenge`
--
ALTER TABLE `challenge`
  ADD CONSTRAINT `fk_challenge_battle` FOREIGN KEY (`battle_id`) REFERENCES `battle` (`battle_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_challenge_card` FOREIGN KEY (`card_id`) REFERENCES `card` (`card_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_challenge_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `notify`
--
ALTER TABLE `notify`
  ADD CONSTRAINT `notify_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `notify_ibfk_2` FOREIGN KEY (`auction_id`) REFERENCES `auction` (`auction_id`),
  ADD CONSTRAINT `notify_ibfk_3` FOREIGN KEY (`wishlist_id`) REFERENCES `wishlist` (`wishlist_id`);

--
-- Constraints for table `participates_in`
--
ALTER TABLE `participates_in`
  ADD CONSTRAINT `participates_in_ibfk_1` FOREIGN KEY (`trade_id`) REFERENCES `trade` (`trade_id`),
  ADD CONSTRAINT `participates_in_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `reward`
--
ALTER TABLE `reward`
  ADD CONSTRAINT `reward_ibfk_1` FOREIGN KEY (`Card`) REFERENCES `card` (`card_id`);

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `fk_chatuser` FOREIGN KEY (`chatuser_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `wins`
--
ALTER TABLE `wins`
  ADD CONSTRAINT `wins_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `wins_ibfk_2` FOREIGN KEY (`reward_id`) REFERENCES `reward` (`reward_id`),
  ADD CONSTRAINT `wins_ibfk_3` FOREIGN KEY (`battle_id`) REFERENCES `battle` (`battle_id`);

--
-- Constraints for table `wishlist`
--
ALTER TABLE `wishlist`
  ADD CONSTRAINT `wishlist_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `wishlist_ibfk_2` FOREIGN KEY (`card_id`) REFERENCES `card` (`card_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
