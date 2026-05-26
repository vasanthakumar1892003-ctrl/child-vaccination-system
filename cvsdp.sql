-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 16, 2026 at 08:48 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cvsdp`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `user_id` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `user_id`, `password`) VALUES
(1, 'admin26', 'pass26');

-- --------------------------------------------------------

--
-- Table structure for table `admin_announcements`
--

CREATE TABLE `admin_announcements` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `audience` varchar(50) DEFAULT 'all',
  `priority` varchar(20) DEFAULT 'normal',
  `posted_on` date NOT NULL,
  `posted_by` varchar(100) DEFAULT 'Admin',
  `is_active` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `chat_messages`
--

CREATE TABLE `chat_messages` (
  `id` int(11) NOT NULL,
  `parent_id` int(11) NOT NULL,
  `hospital_id` int(11) NOT NULL,
  `sender_role` enum('parent','hospital') NOT NULL,
  `message` text NOT NULL,
  `status` enum('sent','seen') DEFAULT NULL,
  `sent_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `chat_messages`
--

INSERT INTO `chat_messages` (`id`, `parent_id`, `hospital_id`, `sender_role`, `message`, `status`, `sent_at`) VALUES
(1, 1, 1, 'parent', 'Hi...', 'seen', '2026-03-08 11:56:44'),
(2, 1, 1, 'hospital', 'Hi! This is Apollo Children Hospital. How can I help you? 😊', 'seen', '2026-03-08 11:56:55'),
(3, 2, 1, 'parent', 'hi', 'seen', '2026-03-09 11:52:41'),
(4, 2, 1, 'hospital', 'Hi! This is Apollo Children Hospital. How can I help you? 😊', 'seen', '2026-03-09 11:52:50'),
(5, 1, 2, 'parent', 'Hi..', 'seen', '2026-03-09 23:48:25'),
(6, 1, 2, 'hospital', 'Hi! This is MIOT International. How can I help you? 😊', 'seen', '2026-03-09 23:48:25'),
(7, 1, 2, 'parent', 'If you do the child vaccinations in your hospital ?', 'seen', '2026-03-09 23:49:54'),
(8, 1, 3, 'parent', 'hi', 'sent', '2026-03-14 14:52:10'),
(9, 1, 3, 'hospital', 'Hi! This is Sri Ramachandra Hospital. How can I help you? 😊', 'seen', '2026-03-14 14:52:10'),
(10, 1, 4, 'parent', 'hi', 'sent', '2026-03-16 10:21:22'),
(11, 1, 4, 'hospital', 'Hi! This is Kovai Medical Centre. How can I help you? 😊', 'seen', '2026-03-16 10:21:22');

-- --------------------------------------------------------

--
-- Table structure for table `hospital`
--

CREATE TABLE `hospital` (
  `id` int(11) NOT NULL,
  `hospital_name` varchar(50) NOT NULL,
  `hospital_type` varchar(50) NOT NULL,
  `license_number` varchar(50) NOT NULL,
  `license_proof` varchar(50) NOT NULL,
  `year_of_establishment` varchar(50) NOT NULL,
  `hospital_logo` varchar(50) NOT NULL,
  `email_id` varchar(50) NOT NULL,
  `hospital_mobile` varchar(10) NOT NULL,
  `hospital_mobile_emergency` varchar(10) NOT NULL,
  `state` varchar(50) NOT NULL,
  `district` varchar(50) NOT NULL,
  `city` varchar(50) NOT NULL,
  `pincode` varchar(50) NOT NULL,
  `street` varchar(50) NOT NULL,
  `area` varchar(50) NOT NULL,
  `bed` varchar(50) NOT NULL,
  `icu` varchar(50) NOT NULL,
  `emergency` varchar(50) NOT NULL,
  `ambulance` varchar(50) NOT NULL,
  `blood_bank` varchar(50) NOT NULL,
  `pharmacy` varchar(50) NOT NULL,
  `service` varchar(50) NOT NULL,
  `working_time` varchar(50) NOT NULL,
  `opd_time` varchar(50) NOT NULL,
  `owner_name` varchar(50) NOT NULL,
  `owner_dob` date NOT NULL,
  `owner_gender` varchar(50) NOT NULL,
  `owner_profile` varchar(50) NOT NULL,
  `id_type` varchar(50) NOT NULL,
  `id_number` varchar(50) NOT NULL,
  `id_proof` varchar(50) NOT NULL,
  `owner_type` varchar(50) NOT NULL,
  `ownership_proof` varchar(50) NOT NULL,
  `status` varchar(50) DEFAULT 'pending',
  `Created_at` varchar(50) DEFAULT current_timestamp(),
  `user_id` varchar(50) DEFAULT NULL,
  `password` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `hospital`
--

INSERT INTO `hospital` (`id`, `hospital_name`, `hospital_type`, `license_number`, `license_proof`, `year_of_establishment`, `hospital_logo`, `email_id`, `hospital_mobile`, `hospital_mobile_emergency`, `state`, `district`, `city`, `pincode`, `street`, `area`, `bed`, `icu`, `emergency`, `ambulance`, `blood_bank`, `pharmacy`, `service`, `working_time`, `opd_time`, `owner_name`, `owner_dob`, `owner_gender`, `owner_profile`, `id_type`, `id_number`, `id_proof`, `owner_type`, `ownership_proof`, `status`, `Created_at`, `user_id`, `password`) VALUES
(1, 'Apollo Children Hospital', 'Private', 'LIC-APL-2001', 'license proof_1.jpg', '2001', 'apollo.jpg', 'apollo.chennai@gmail.com', '9840012345', '9840012346', 'Tamil Nadu', 'Chennai', 'Chennai', '600001', '21 Greams Road', 'Thousand Lights', '200', 'Available', 'Available', 'Available', 'Available', 'Available', 'Yes', '24x7', '8AM-8PM', 'Dr. Ravi Kumar', '1970-05-14', 'Male', 'man.png', 'Aadhar', 'ADHR-1001-APLO', 'Aadhar.jpg', 'Individual', 'apollo.jpg', 'approved', '2026-03-07 23:26:06', 'hCvS1', 'APO1K7lb'),
(2, 'MIOT International', 'Private', 'LIC-MIOT-1995', 'license proof.png', '1995', 'MITO.png', 'miot.hospital@gmail.com', '9841023456', '9841023457', 'Tamil Nadu', 'Chennai', 'Chennai', '600089', '4/112 Mount Poonamallee Road', 'Manapakkam', '350', 'Available', 'Available', 'Available', 'Available', 'Available', 'Yes', '24x7', '9AM-6PM', 'Dr. Suresh Manohar', '1968-11-20', 'Male', 'man.png', 'Aadhar', 'ADHR-2002-MIOT', 'Aadhar.jpg', 'Trust', 'Ownership proof.jpg', 'approved', '2026-03-07 23:26:06', 'hCvS2', 'MIO2Lvir'),
(3, 'Sri Ramachandra Hospital', 'Government', 'LIC-SRM-1985', 'license proof.png', '1985', 'Sri Ramachandra.png', 'srmhospital@gov.in', '9842034567', '9842034568', 'Tamil Nadu', 'Chennai', 'Chennai', '600116', 'No.1, Ramachandra Nagar', 'Porur', '500', 'Available', 'Available', 'Available', 'Available', 'Available', 'Yes', '24x7', '8AM-5PM', 'Dr. Priya Chandran', '1975-03-08', 'Female', 'man.png', 'Aadhar', 'ADHR-3003-SRM', 'Aadhar.jpg', 'Government', 'Ownership proof.jpg', 'approved', '2026-03-07 23:26:06', 'hCvS3', 'SRI3LCXo'),
(4, 'Kovai Medical Centre', 'Private', 'LIC-KMC-2005', 'license proof.png', '2005', 'KMCH.png', 'kmchospital@gmail.com', '9843045678', '9843045679', 'Tamil Nadu', 'Coimbatore', 'Coimbatore', '641014', 'Avanashi Road', 'Peelamedu', '300', 'Available', 'Available', 'Available', 'Available', 'Available', 'Yes', '24x7', '8AM-8PM', 'Dr. Anand Raj', '1972-07-19', 'Male', 'man.png', 'Aadhar', 'ADHR-4004-KMC', 'Aadhar.jpg', 'Individual', 'Ownership proof.jpg', 'approved', '2026-03-07 23:26:06', 'hCvS4', 'KOV4uFIs'),
(5, 'Meenakshi Mission Hospital', 'Private', 'LIC-MMH-2010', 'license proof.png', '2010', 'Meenakshi.png', 'mmhospital@gmail.com', '9844056789', '9844056790', 'Tamil Nadu', 'Madurai', 'Madurai', '625107', 'Lake Area', 'Melur Road', '250', 'Available', 'Available', 'Available', 'Available', 'Available', 'Yes', '24x7', '9AM-7PM', 'Dr. Kavitha Selvan', '1980-01-25', 'Female', 'man.png', 'Aadhar', 'VOTE-5005-MMH', 'Aadhar.jpg', 'Partnership', 'Ownership proof.jpg', 'approved', '2026-03-07 23:26:06', 'hCvS5', 'MEE5QRIe'),
(6, 'PSG Hospitals', 'Private', 'LIC-PSG-2000', 'license proof.png', '2000', 'PSG.png', 'psghospital@gmail.com', '9845067890', '9845067891', 'Tamil Nadu', 'Coimbatore', 'Coimbatore', '641004', 'Peelamedu', 'Avinashi Road', '400', 'Available', 'Available', 'Available', 'Available', 'Available', 'Yes', '24x7', '8AM-9PM', 'Dr. Vikram Narayanan', '1965-09-12', 'Male', 'man.png', 'Aadhar', 'ADHR-6006-PSG', 'Aadhar.jpg', 'Trust', 'Ownership proof.jpg', 'approved', '2026-03-07 23:26:06', 'hCvS6', 'PSG6efUs'),
(7, 'Kauvery Hospital', 'Private', 'LIC-KAU-2008', 'license proof.png', '2008', 'Kauvery.png', 'kauvery@gmail.com', '9846078901', '9846078902', 'Tamil Nadu', 'Trichy', 'Tiruchirappalli', '620018', 'Tennur', 'Main Road', '180', 'Available', 'Available', 'Available', 'Available', 'Available', 'Yes', '24x7', '8AM-8PM', 'Dr. Selvi Rangan', '1978-06-30', 'Female', 'man.png', 'Aadhar', 'ADHR-7007-KAU', 'Aadhar.jpg', 'Individual', 'Ownership proof.jpg', 'pending', '2026-03-07 23:26:06', 'kau007', 'Kauvery@7'),
(8, 'Government Rajaji Hospital', 'Government', 'LIC-GRH-1960', 'license proof.png', '1960', 'Government Rajaji.gif', 'rajajihospital@gov.in', '9847089012', '9847089013', 'Tamil Nadu', 'Madurai', 'Madurai', '625020', 'Panagal Road', 'Madurai Central', '1000', 'Available', 'Available', 'Available', 'Available', 'Available', 'Yes', '24x7', '8AM-4PM', 'Dr. Murugan Arumugam', '1960-04-17', 'Male', 'man.png', 'Aadhar', 'ADHR-8008-GRH', 'Aadhar.jpg', 'Government', 'Ownership proof.jpg', 'pending', '2026-03-07 23:26:06', 'grh008', 'GRH@Gov008'),
(9, 'Annai Arul Hospital', 'Private', 'LIC-AAH-2015', 'license proof.png', '2015', 'Annai Arul.jpg', 'annaiarul@gmail.com', '9848090123', '9848090124', 'Tamil Nadu', 'Salem', 'Salem', '636004', 'Five Roads', 'Shevapet', '120', 'Available', 'Available', 'Available', 'Available', 'Available', 'Yes', '8AM-10PM', '9AM-6PM', 'Dr. Nirmala Devi', '1983-12-05', 'Female', 'man.png', 'Aadhar', 'ADHR-9009-AAH', 'Aadhar.jpg', 'Individual', 'Ownership proof.jpg', 'pending', '2026-03-07 23:26:06', 'aah009', 'Annai@009'),
(10, 'Billroth Hospitals', 'Private', 'LIC-BIL-2003', 'license proof.png', '2003', 'Billroth.jpg', 'billroth@gmail.com', '9849001234', '9849001235', 'Tamil Nadu', 'Chennai', 'Chennai', '600010', '43 Lakshmi Talkies Road', 'Shenoy Nagar', '220', 'Available', 'Available', 'Available', 'Available', 'Available', 'Yes', '24x7', '8AM-8PM', 'Dr. Harish Balaji', '1977-08-22', 'Male', 'man.png', 'Aadhar', 'ADHR-1010-BIL', 'Aadhar.jpg', 'Partnership', 'Ownership proof.jpg', 'pending', '2026-03-07 23:26:06', 'bil010', 'Billroth@10');

-- --------------------------------------------------------

--
-- Table structure for table `hospital_appointment`
--

CREATE TABLE `hospital_appointment` (
  `id` int(11) NOT NULL,
  `p_name` varchar(50) NOT NULL,
  `p_gender` varchar(50) NOT NULL,
  `email_id` varchar(100) NOT NULL,
  `mobile` varchar(50) NOT NULL,
  `c_name` varchar(50) NOT NULL,
  `c_gender` varchar(50) NOT NULL,
  `c_dob` varchar(50) NOT NULL,
  `age_group` varchar(50) NOT NULL,
  `vaccination_name` varchar(300) NOT NULL,
  `appointment_date` varchar(50) NOT NULL,
  `hospital_name` varchar(50) NOT NULL,
  `status` varchar(50) DEFAULT 'pending',
  `create_at` varchar(50) DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `hospital_appointment`
--

INSERT INTO `hospital_appointment` (`id`, `p_name`, `p_gender`, `email_id`, `mobile`, `c_name`, `c_gender`, `c_dob`, `age_group`, `vaccination_name`, `appointment_date`, `hospital_name`, `status`, `create_at`) VALUES
(1, 'Ramesh Kumar', 'Male', 'ramesh.kumar@gmail.com', '9500112233', 'kumar', 'Male', '2024-10-06', '2 Years', 'Typhoid Conjugate Vaccine (TCV) , Meningococcal (MCV) ( 1 st DOSE ) & Varicella (2nd DOSE ) & Vitamin A ( 3rd DOSE ) & Hepatitis A (HepA) ( BOOSTER )', '2026-06-10', 'Apollo Children Hospital', 'pending', '2026-03-08 11:14:35'),
(2, 'Ramesh Kumar', 'Male', 'ramesh.kumar@gmail.com', '9500112233', 'vasanth', 'Male', '2025-09-18', '6 Months', 'MR (Measles-Rubella) , Japanese Encephalitis (JE) , Typhoid ,  Influenza (Flu) ( 1st DOSE )', '2026-03-12', 'Apollo Children Hospital', 'completed', '2026-03-08 11:29:15'),
(3, 'Ramesh Kumar', 'Male', 'ramesh.kumar@gmail.com', '9500112233', 'Golu', 'Male', '2026-01-27', '6 Weeks', 'DTaP , IPV , Hib , Rotavirus (RV) , PCV ( 1st DOSE ) & HepB  ( 2nd DOSE )', '2026-03-17', 'Apollo Children Hospital', 'pending', '2026-03-09 23:08:43'),
(4, 'Ramesh Kumar', 'Male', 'ramesh.kumar@gmail.com', '9500112233', 'ganesh', 'Male', '2026-03-13', 'At Birth', 'BCG , HepB ( 1st DOSE ) & OPV ( 0 DOSE )', '2026-03-13', 'Apollo Children Hospital', 'completed', '2026-03-11 10:23:42'),
(5, 'Ramesh Kumar', 'Male', 'ramesh.kumar@gmail.com', '9500112233', 'palani', 'Male', '2026-03-16', 'At Birth', 'BCG , HepB ( 1st DOSE ) & OPV ( 0 DOSE )', '2026-03-16', 'Apollo Children Hospital', 'completed', '2026-03-16 12:59:34');

-- --------------------------------------------------------

--
-- Table structure for table `hospital_feedback`
--

CREATE TABLE `hospital_feedback` (
  `id` int(11) NOT NULL,
  `hospital_name` varchar(200) NOT NULL,
  `email` varchar(200) NOT NULL,
  `contact_person` varchar(200) DEFAULT NULL,
  `rating` int(11) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `feedback_text` text NOT NULL,
  `suggestion` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `hospital_support_ticket`
--

CREATE TABLE `hospital_support_ticket` (
  `ticket_id` int(11) NOT NULL,
  `hospital_id` int(11) NOT NULL,
  `hospital_name` varchar(100) NOT NULL,
  `contact_email` varchar(100) NOT NULL,
  `issue_category` varchar(100) NOT NULL,
  `priority` varchar(50) NOT NULL,
  `issue_description` text NOT NULL,
  `status` varchar(30) DEFAULT 'open',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `manage_child`
--

CREATE TABLE `manage_child` (
  `id` int(11) NOT NULL,
  `child_name` varchar(50) NOT NULL,
  `child_dob` varchar(50) NOT NULL,
  `child_gender` varchar(50) NOT NULL,
  `done_vaccin` varchar(50) DEFAULT 'None',
  `vaccin_age` varchar(50) DEFAULT 'None',
  `vaccin_name` varchar(250) DEFAULT 'None',
  `last_vaccinedate` varchar(50) DEFAULT 'None',
  `parent_name` varchar(50) NOT NULL,
  `parent_type` varchar(50) NOT NULL,
  `parent_gender` varchar(50) NOT NULL,
  `email_id` varchar(50) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `manage_child`
--

INSERT INTO `manage_child` (`id`, `child_name`, `child_dob`, `child_gender`, `done_vaccin`, `vaccin_age`, `vaccin_name`, `last_vaccinedate`, `parent_name`, `parent_type`, `parent_gender`, `email_id`, `created_at`) VALUES
(1, 'kumar', '2024-06-10', 'Male', '9', '18 Months', 'Hepatitis A (HepA) , Vitamin A ( 2nd DOSE ) & DTwP/DTaP Booster , OPV Booster ( 1st BOOSTER)', '2025-10-12', 'Ramesh Kumar', 'Father', 'Male', 'ramesh.kumar@gmail.com', '2026-03-08 05:28:32'),
(2, 'Vasanth', '2025-09-18', 'Male', '4', '14 Weeks', 'DTaP , IPV , Hib , Rotavirus (RV) , PCV ( 3 rd DOSE )', '2025-12-25', 'Ramesh Kumar', 'Father', 'Male', 'ramesh.kumar@gmail.com', '2026-03-08 05:50:54'),
(3, 'Golu', '2026-01-27', 'Male', '1', 'At Birth', 'BCG , HepB ( 1st DOSE ) & OPV ( 0 DOSE )', '2026-01-27', 'Ramesh Kumar', 'Father', 'Male', 'ramesh.kumar@gmail.com', '2026-03-09 13:01:54'),
(4, 'Raja', '2026-03-10', 'Male', '0', '', '', '', 'Ramesh Kumar', 'Father', 'Male', 'ramesh.kumar@gmail.com', '2026-03-10 04:40:42'),
(5, 'sree', '2026-03-10', 'Female', '0', '', '', '', 'Ramesh Kumar', 'Father', 'Male', 'ramesh.kumar@gmail.com', '2026-03-10 07:25:30'),
(6, 'ganesh', '2026-03-13', 'Male', '0', '', '', '', 'Ramesh Kumar', 'Father', 'Male', 'ramesh.kumar@gmail.com', '2026-03-11 04:50:49'),
(7, 'palani', '2026-03-16', 'Male', '0', '', '', '', 'Ramesh Kumar', 'Father', 'Male', 'ramesh.kumar@gmail.com', '2026-03-11 06:36:01');

-- --------------------------------------------------------

--
-- Table structure for table `parent`
--

CREATE TABLE `parent` (
  `id` int(11) NOT NULL,
  `parent_type` varchar(50) NOT NULL,
  `parent_name` varchar(50) NOT NULL,
  `parent_gender` varchar(50) NOT NULL,
  `parent_dob` varchar(50) NOT NULL,
  `parent_mobile` varchar(10) NOT NULL,
  `email_id` varchar(50) NOT NULL,
  `parent_profile` varchar(50) NOT NULL,
  `alternate_mobile` varchar(10) NOT NULL,
  `state` varchar(50) NOT NULL,
  `district` varchar(50) NOT NULL,
  `city` varchar(50) NOT NULL,
  `pincode` varchar(50) NOT NULL,
  `street` varchar(50) NOT NULL,
  `area` varchar(50) NOT NULL,
  `id_type` varchar(50) NOT NULL,
  `id_number` varchar(50) NOT NULL,
  `id_proof` varchar(50) NOT NULL,
  `child_order` varchar(50) NOT NULL,
  `status` varchar(50) DEFAULT 'pending',
  `Created_at` varchar(50) DEFAULT current_timestamp(),
  `user_id` varchar(50) DEFAULT NULL,
  `password` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `parent`
--

INSERT INTO `parent` (`id`, `parent_type`, `parent_name`, `parent_gender`, `parent_dob`, `parent_mobile`, `email_id`, `parent_profile`, `alternate_mobile`, `state`, `district`, `city`, `pincode`, `street`, `area`, `id_type`, `id_number`, `id_proof`, `child_order`, `status`, `Created_at`, `user_id`, `password`) VALUES
(1, 'Father', 'Ramesh Kumar', 'Male', '1985-03-15', '9500112233', 'ramesh.kumar@gmail.com', 'man.png', '9500112234', 'Tamil Nadu', 'Chennai', 'Chennai', '600001', '12 Anna Nagar East', 'Anna Nagar', 'Aadhar', '123654789012', 'Aadhar.jpg', 'Fifth Child', 'approved', '2026-03-07 23:27:11', 'pCvS1', 'RA1sXUN'),
(2, 'Mother', 'Priya Suresh', 'Female', '1990-07-20', '9501223344', 'priya.suresh@gmail.com', 'women.jpg', '9501223345', 'Tamil Nadu', 'Chennai', 'Chennai', '600026', '5B Brigade Road', 'Adyar', 'Aadhar', 'ADHR-P002', 'Aadhar.jpg', 'Two Childs', 'approved', '2026-03-07 23:27:11', 'pCvS2', 'PR2HE8U'),
(3, 'Father', 'Senthil Murugan', 'Male', '1982-11-10', '9502334455', 'senthil.m@gmail.com', 'man.png', '9502334456', 'Tamil Nadu', 'Coimbatore', 'Coimbatore', '641014', '22 Saibaba Colony', 'Saibaba Colony', 'Aadhar', 'ADHR-P003', 'Aadhar.jpg', 'One Child', 'approved', '2026-03-07 23:27:11', 'pCvS3', 'SE3MQYI'),
(4, 'Mother', 'Lakshmi Anand', 'Female', '1993-05-25', '9503445566', 'lakshmi.anand@gmail.com', 'women.jpg', '9503445567', 'Tamil Nadu', 'Madurai', 'Madurai', '625001', '8 North Masi Street', 'North Masi', 'Aadhar', 'ADHR-P004', 'Aadhar.jpg', 'One Child', 'approved', '2026-03-07 23:27:11', 'pCvS4', 'LA4Seju'),
(5, 'Father', 'Dinesh Raj', 'Male', '1988-09-05', '9504556677', 'dinesh.raj@gmail.com', 'man.png', '9504556678', 'Tamil Nadu', 'Trichy', 'Tiruchirappalli', '620017', '14 Thillai Nagar', 'Thillai Nagar', 'Aadhar', 'ADHR-P005', 'Aadhar.jpg', 'Three Childs', 'approved', '2026-03-07 23:27:11', 'pCvS5', 'DI5dr5q'),
(6, 'Mother', 'Meena Vijay', 'Female', '1991-02-14', '9505667788', 'meena.vijay@gmail.com', 'women.jpg', '9505667789', 'Tamil Nadu', 'Salem', 'Salem', '636005', '3 Fairlands', 'Fairlands', 'Aadhar', 'ADHR-P006', 'Aadhar.jpg', 'Two Childs', 'approved', '2026-03-07 23:27:11', 'pCvS6', 'ME60IHK'),
(7, 'Father', 'Arjun Krishnan', 'Male', '1984-06-18', '9506778899', 'arjun.k@gmail.com', 'man.png', '9506778900', 'Tamil Nadu', 'Chennai', 'Chennai', '600040', '9 Velachery Main Road', 'Velachery', 'Aadhar', 'ADHR-P007', 'Aadhar.jpg', 'One Child', 'approved', '2026-03-07 23:27:11', 'pCvS7', 'AR77Zep'),
(8, 'Mother', 'Divya Balasubramaniam', 'Female', '1995-10-30', '9507889900', 'divya.balu@gmail.com', 'women.jpg', '9507889901', 'Tamil Nadu', 'Coimbatore', 'Coimbatore', '641002', '17 RS Puram', 'RS Puram', 'Aadhar', 'ADHR-P008', 'Aadhar.jpg', 'One Child', 'pending', '2026-03-07 23:27:11', 'par008', 'Div@008'),
(9, 'Father', 'Karthik Selvam', 'Male', '1986-04-22', '9508990011', 'karthik.s@gmail.com', 'man.png', '9508990012', 'Tamil Nadu', 'Tirunelveli', 'Tirunelveli', '627001', '6 Palayamkottai Rd', 'Palayamkottai', 'Aadhar', 'ADHR-P009', 'Aadhar.jpg', 'One Child', 'pending', '2026-03-07 23:27:11', 'par009', 'Kar@009'),
(10, 'Mother', 'Anitha Prakash', 'Female', '1989-08-11', '9509001122', 'anitha.p@gmail.com', 'anitha_pic.jpg', '9509001123', 'Tamil Nadu', 'Erode', 'Erode', '638001', '20 Perundurai Road', 'Erode Town', 'Aadhar', 'ADHR-P010', 'Aadhar.jpg', '1st', 'pending', '2026-03-07 23:27:11', 'par010', 'Ani@010');

-- --------------------------------------------------------

--
-- Table structure for table `parentform`
--

CREATE TABLE `parentform` (
  `id` int(11) NOT NULL,
  `p_name` varchar(50) NOT NULL,
  `p_type` varchar(50) NOT NULL,
  `p_gender` varchar(50) NOT NULL,
  `mobile` varchar(50) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `aadhaar_number` varchar(50) NOT NULL,
  `c_name` varchar(50) NOT NULL,
  `c_gender` varchar(50) NOT NULL,
  `c_dob` varchar(50) NOT NULL,
  `c_order` varchar(50) NOT NULL,
  `vaccin` varchar(50) NOT NULL,
  `vaccin_age` varchar(50) DEFAULT 'None',
  `vaccination` varchar(250) DEFAULT 'None',
  `appointment_date` varchar(50) NOT NULL,
  `age_group` varchar(50) NOT NULL,
  `vaccine_name` varchar(250) NOT NULL,
  `address` varchar(100) NOT NULL,
  `district` varchar(50) NOT NULL,
  `pincode` varchar(50) NOT NULL,
  `hospital_name` varchar(50) NOT NULL,
  `status` varchar(50) DEFAULT 'pending',
  `created_at` varchar(50) DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `parentform`
--

INSERT INTO `parentform` (`id`, `p_name`, `p_type`, `p_gender`, `mobile`, `email`, `aadhaar_number`, `c_name`, `c_gender`, `c_dob`, `c_order`, `vaccin`, `vaccin_age`, `vaccination`, `appointment_date`, `age_group`, `vaccine_name`, `address`, `district`, `pincode`, `hospital_name`, `status`, `created_at`) VALUES
(1, 'Ramesh Kumar', 'Father', 'Male', '9500112233', 'ramesh.kumar@gmail.com', '123654789012', 'kumar', 'Male', '2024-10-06', '1', 'Yes', '18 Months', 'DTwP/DTaP Booster, OPV Booster, Hepatitis A, Vitamin A', '2026-06-10', '2 Years', 'Typhoid Conjugate Vaccine (TCV) , Meningococcal (MCV) ( 1 st DOSE ) & Varicella (2nd DOSE ) & Vitamin A ( 3rd DOSE ) & Hepatitis A (HepA) ( BOOSTER )', 'Chennai', 'Chennai', '600001', 'Apollo Children Hospital', 'approved', '2026-03-08 11:13:35'),
(2, 'Ramesh Kumar', 'Father', 'Male', '9500112233', 'ramesh.kumar@gmail.com', '123654789012', 'vasanth', 'Male', '2025-09-18', '2', 'Yes', '14 Weeks', 'DTaP, IPV, Hib, Rotavirus (RV), PCV', '2026-03-19', '6 Months', 'MR (Measles-Rubella) , Japanese Encephalitis (JE) , Typhoid , Influenza (Flu) ( 1st DOSE )', 'Chennai', 'Chennai', '600001', 'Apollo Children Hospital', 'rescheduled', '2026-03-08 11:27:29'),
(3, 'Ramesh Kumar', 'Father', 'Male', '9500112233', 'ramesh.kumar@gmail.com', '123654789012', 'Golu', 'Male', '2026-01-27', '3', 'Yes', 'At Birth', 'BCG, HepB, OPV', '2026-03-10', '6 Weeks', 'DTaP , IPV , Hib , Rotavirus (RV) , PCV ( 1st DOSE ) & HepB ( 2nd DOSE )', 'Chennai', 'Chennai', '600001', 'Apollo Children Hospital', 'approved', '2026-03-09 18:58:08'),
(4, 'Ramesh Kumar', 'Father', 'Male', '9500112233', 'ramesh.kumar@gmail.com', '123654789012', 'ganesh', 'Male', '2026-03-13', '5', 'No', '', 'None', '2026-03-13', 'At Birth', 'BCG , HepB ( 1st DOSE ) & OPV ( 0 DOSE )', '12 Anna Nagar East, Anna Nagar, Chennai', 'Chennai', '600001', 'Apollo Children Hospital', 'approved', '2026-03-11 10:22:36'),
(5, 'Ramesh Kumar', 'Father', 'Male', '9500112233', 'ramesh.kumar@gmail.com', '123654789012', 'Vasanth', 'Male', '2025-09-18', '2', 'No', '', 'None', '2026-03-12', '6 Months', 'MR (Measles-Rubella) , Japanese Encephalitis (JE) , Typhoid ,  Influenza (Flu) ( 1st DOSE )', '12 Anna Nagar East, Anna Nagar, Chennai', 'Chennai', '600001', 'Apollo Children Hospital', 'rescheduled', '2026-03-11 10:27:37'),
(6, 'Ramesh Kumar', 'Father', 'Male', '9500112233', 'ramesh.kumar@gmail.com', '123654789012', 'palani', 'Male', '2026-03-13', '1', 'No', '', 'None', '2026-03-13', 'At Birth', 'BCG , HepB ( 1st DOSE ) & OPV ( 0 DOSE )', '12 Anna Nagar East, Anna Nagar, Chennai', 'Chennai', '600001', 'Apollo Children Hospital', 'pending', '2026-03-11 12:06:42'),
(7, 'Ramesh Kumar', 'Father', 'Male', '9500112233', 'ramesh.kumar@gmail.com', '123654789012', 'Golu', 'Male', '2026-01-27', '1', 'No', '', 'None', '2026-03-17', '6 Weeks', 'DTaP , IPV , Hib , Rotavirus (RV) , PCV ( 1st DOSE ) & HepB  ( 2nd DOSE )', '12 Anna Nagar East, Anna Nagar, Chennai', 'Chennai', '600001', 'Apollo Children Hospital', 'rescheduled', '2026-03-16 11:05:36'),
(8, 'Ramesh Kumar', 'Father', 'Male', '9500112233', 'ramesh.kumar@gmail.com', '123654789012', 'palani', 'Male', '2026-03-16', '5', 'No', '', 'None', '2026-03-16', 'At Birth', 'BCG , HepB ( 1st DOSE ) & OPV ( 0 DOSE )', '12 Anna Nagar East, Anna Nagar, Chennai', 'Chennai', '600001', 'Apollo Children Hospital', 'approved', '2026-03-16 12:58:53');

-- --------------------------------------------------------

--
-- Table structure for table `parent_feedback`
--

CREATE TABLE `parent_feedback` (
  `id` int(11) NOT NULL,
  `parent_name` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `child_name` varchar(100) DEFAULT NULL,
  `hospital_name` varchar(150) DEFAULT NULL,
  `rating` int(1) NOT NULL CHECK (`rating` between 1 and 5),
  `category` varchar(100) DEFAULT NULL,
  `feedback_text` text NOT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `parent_support_ticket`
--

CREATE TABLE `parent_support_ticket` (
  `id` int(11) NOT NULL,
  `parent_id` varchar(20) DEFAULT '',
  `parent_name` varchar(100) NOT NULL,
  `contact_email` varchar(100) NOT NULL,
  `issue_category` varchar(100) NOT NULL,
  `priority` varchar(50) NOT NULL,
  `description` text NOT NULL,
  `status` varchar(30) DEFAULT 'open',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `public_support_ticket`
--

CREATE TABLE `public_support_ticket` (
  `ticket_id` int(11) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `contact_email` varchar(100) NOT NULL,
  `user_role` varchar(50) NOT NULL,
  `issue_category` varchar(100) NOT NULL,
  `priority` varchar(50) NOT NULL,
  `description` text NOT NULL,
  `status` varchar(30) DEFAULT 'open',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `vaccination_schedule`
--

CREATE TABLE `vaccination_schedule` (
  `id` int(11) NOT NULL,
  `vaccine_name` varchar(300) NOT NULL,
  `age_group` varchar(50) NOT NULL,
  `description` varchar(500) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `vaccination_schedule`
--

INSERT INTO `vaccination_schedule` (`id`, `vaccine_name`, `age_group`, `description`, `created_at`) VALUES
(1, 'BCG , HepB ( 1st DOSE ) & OPV ( 0 DOSE )', 'At Birth', 'Protection against Tuberculosis , Hepatitis B (Liver infection) and against Polio', '2026-03-06 10:05:53'),
(2, 'DTaP , IPV , Hib , Rotavirus (RV) , PCV ( 1st DOSE ) & HepB  ( 2nd DOSE )', '6 Weeks', 'Protection against Diphtheria, Tetanus, Pertussis and Polio , Hepatitis B , Meningitis , \r\n\r\nRotavirus , Pneumonia and Hepatitis B', '2026-03-06 10:11:22'),
(3, 'DTaP , IPV , Hib , Rotavirus (RV) , PCV ( 2 nd DOSE )', '10 Weeks', 'Reinforces the first dose series - Diphtheria, Tetanus, Pertussis and Polio , Meningitis , Rotavirus , Pneumonia', '2026-03-06 10:15:25'),
(4, 'DTaP , IPV , Hib , Rotavirus (RV) , PCV ( 3 rd DOSE )', '14 Weeks', 'Sustains long-term immunity - Diphtheria, Tetanus, Pertussis and Polio , Meningitis , Rotavirus , Pneumonia', '2026-03-06 10:16:55'),
(5, 'MR (Measles-Rubella) , Japanese Encephalitis (JE) , Typhoid ,  Influenza (Flu) ( 1st DOSE )', '6 Months', 'Protection against Measles and Rubella , Japanese Encephalitis , Typhoid Fever ,  Seasonal Flu ( 1 st DOSE )', '2026-03-06 10:20:30'),
(6, 'Varicella , Hepatitis A (HepA) ( 1st DOSE ) , MMR  ( 2nd DOSE ) & PCV Booster ,  DTaP Booster ( BOOSTER )', '12 Months', 'Protection against Chickenpox , Hepatitis A and Mumps, Measles, Rubella and Booster dose for Pneumonia protection , Diphtheria, Tetanus, Pertussis', '2026-03-06 10:25:44'),
(7, 'Measles (MCV1) , Vitamin A ( 1st DOSE ) & OPV ( 3 rd DOSE )', '9 Months', 'Protection against Measles - first dose under national immunization schedule , Vitamin A supplementation to prevent deficiency and boost immunity and Third dose of Oral Polio Vaccine for continued Polio protection', '2026-03-06 10:29:30'),
(8, 'MMR , Varicella ( 1 st DOSE ) & Hib Booster , PCV Booster ( BOOSTER )', '15 Months', 'Protection against Measles, Mumps and Rubella - first MMR , Chickenpox - first dose recommended at 15 months AND Booster dose for Haemophilus influenzae type b - Meningitis protection , Pneumococcal vaccine - Pneumonia protection', '2026-03-06 10:33:07'),
(9, 'Hepatitis A (HepA) , Vitamin A ( 2nd DOSE ) & DTwP/DTaP Booster ,  OPV Booster ( 1st BOOSTER )', '18 Months', 'Second dose of Hepatitis A vaccine - completes the HepA series , vitamin A supplementation dose for immunity and eye health and First booster for Diphtheria, Tetanus and Pertussis protection , Oral Polio Vaccine', '2026-03-06 12:10:23'),
(10, 'Typhoid Conjugate Vaccine (TCV) , Meningococcal (MCV) ( 1 st DOSE ) &  Varicella (2nd DOSE ) &  Vitamin A ( 3rd DOSE ) &  Hepatitis A (HepA)  ( BOOSTER )', '2 Years', 'Protection against Typhoid Fever - recommended from 2 years onwards\r\nVaccine Name: Meningococcal (MCV) , Meningococcal disease and bacterial Meningitis and Second dose of Chickenpox vaccine for complete immunity and Continued Vitamin A supplementation every 6 months up to 5 years and Booster dose of Hepatitis A for long-term liver disease protection', '2026-03-06 12:23:52'),
(11, 'Varicella ( 2 nd DOSE ) & MMR ( 3 rd DOSE ) &  OPV ( BOOSTER ) & DTaP ( 2 nd BOOSTER )', '4-6 Years', 'Final preschool booster for Chickenpox and Mumps, Measles, Rubella and Polio and Diphtheria, Tetanus, Pertussis', '2026-03-06 12:29:26'),
(12, 'HPV ( 1 st, 2 nd DOSES ) & Tdap/Td ( BOOSTER )', '10 Years', 'Protection against HPV - prevents various cancers , Second dose of HPV vaccine series and Reinforcement of Tetanus and Diphtheria immunity', '2026-03-06 12:33:15');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `admin_announcements`
--
ALTER TABLE `admin_announcements`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `chat_messages`
--
ALTER TABLE `chat_messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_conversation` (`parent_id`,`hospital_id`),
  ADD KEY `idx_sent_at` (`sent_at`);

--
-- Indexes for table `hospital`
--
ALTER TABLE `hospital`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `license_number` (`license_number`);

--
-- Indexes for table `hospital_appointment`
--
ALTER TABLE `hospital_appointment`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `hospital_feedback`
--
ALTER TABLE `hospital_feedback`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `hospital_support_ticket`
--
ALTER TABLE `hospital_support_ticket`
  ADD PRIMARY KEY (`ticket_id`);

--
-- Indexes for table `manage_child`
--
ALTER TABLE `manage_child`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `parent`
--
ALTER TABLE `parent`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email_id` (`email_id`),
  ADD UNIQUE KEY `id_number` (`id_number`);

--
-- Indexes for table `parentform`
--
ALTER TABLE `parentform`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `parent_feedback`
--
ALTER TABLE `parent_feedback`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `parent_support_ticket`
--
ALTER TABLE `parent_support_ticket`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `public_support_ticket`
--
ALTER TABLE `public_support_ticket`
  ADD PRIMARY KEY (`ticket_id`);

--
-- Indexes for table `vaccination_schedule`
--
ALTER TABLE `vaccination_schedule`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `admin_announcements`
--
ALTER TABLE `admin_announcements`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `chat_messages`
--
ALTER TABLE `chat_messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `hospital`
--
ALTER TABLE `hospital`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `hospital_appointment`
--
ALTER TABLE `hospital_appointment`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `hospital_feedback`
--
ALTER TABLE `hospital_feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `hospital_support_ticket`
--
ALTER TABLE `hospital_support_ticket`
  MODIFY `ticket_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `manage_child`
--
ALTER TABLE `manage_child`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `parent`
--
ALTER TABLE `parent`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `parentform`
--
ALTER TABLE `parentform`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `parent_feedback`
--
ALTER TABLE `parent_feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `parent_support_ticket`
--
ALTER TABLE `parent_support_ticket`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `public_support_ticket`
--
ALTER TABLE `public_support_ticket`
  MODIFY `ticket_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `vaccination_schedule`
--
ALTER TABLE `vaccination_schedule`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=83;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
