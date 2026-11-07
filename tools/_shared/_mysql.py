import pymysql

SQL1_INIT = """

START TRANSACTION;
DROP DATABASE IF EXISTS `campwiz`;
CREATE DATABASE `campwiz`;
USE `campwiz`;
CREATE TABLE `user` (
    `id`	INT(11) NOT NULL PRIMARY KEY,
    `username`	TEXT NOT NULL UNIQUE,
    `rights`	INT(11) NOT NULL DEFAULT 1,
    `created_at`	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `article_count`	INT(11) DEFAULT 0,
    `category_count`	INT(11) DEFAULT 0,
    `task_count`	INT(11) DEFAULT 0,
    `campaign_count`	INT(11) DEFAULT 0,
    `jury_count`	INT(11) DEFAULT 0,
    `jury_vote_count`	INT(11) DEFAULT 0,
    `submission_count`	INT(11) DEFAULT 0,
    `points`	INT(11) DEFAULT 0,
    `wiki_registered_at`	TIMESTAMP NULL DEFAULT NULL,
    `feedback_ui_score`	INT(11) DEFAULT 0,
    `feedback_speed_score`	INT(11) DEFAULT 0,
    `feedback_note`	TEXT DEFAULT ''
);    
CREATE TABLE IF NOT EXISTS `campaign` (
    `id`    INT(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name`    TEXT NOT NULL,
    `language`    TEXT NOT NULL,
    `start_at`    TEXT NOT NULL,
    `end_at`    TEXT NOT NULL,
    `created_at`    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `created_by_id`    INT(11) NOT NULL,
    `approved_by`    INT(11) NULL DEFAULT NULL,
    `approved_at`    TIMESTAMP NULL DEFAULT NULL,
    `description`    TEXT NULL DEFAULT NULL,
    `rules`    TEXT NULL DEFAULT NULL,
    `blacklist`    TEXT NULL DEFAULT NULL,
    `image`    TEXT NULL DEFAULT NULL,
    `jury`    TEXT NULL DEFAULT NULL,
    `status`    TEXT NOT NULL DEFAULT 'pending',
    `maximumSubmissionOfSameArticle`   INT(11) NOT NULL DEFAULT 1,
    `allowExpansions`   BOOLEAN NOT NULL DEFAULT TRUE,
    `minimumTotalBytes` INT(11) NOT NULL DEFAULT 4000,
    `minimumTotalWords` INT(11) NOT NULL DEFAULT 400,
    `minimumAddedBytes` INT(11) NOT NULL DEFAULT 4000,
    `minimumAddedWords` INT(11) NOT NULL DEFAULT 400,
    `secretBallot`  BOOLEAN NOT NULL DEFAULT TRUE,
    `allowJuryToParticipate`    BOOLEAN NOT NULL DEFAULT TRUE,
    `allowMultipleJudgement`    BOOLEAN NOT NULL DEFAULT TRUE,
    `total_submissions` INT(11) NOT NULL DEFAULT 0,
    `total_newly_created` INT(11) NOT NULL DEFAULT 0,
    `total_points` INT(11) NOT NULL DEFAULT 0,
    `total_new_users` INT(11) NOT NULL DEFAULT 0,
    CONSTRAINT `campaign_approved_by_fkey` FOREIGN KEY(`approved_by`) REFERENCES `user`(`id`) ON DELETE SET NULL,
    CONSTRAINT `campaign_created_by_id_fkey` FOREIGN KEY(`created_by_id`) REFERENCES `user`(`id`) ON DELETE SET NULL
);


CREATE INDEX IF NOT EXISTS `campaign_language_index` ON `campaign` (`language`);
CREATE TABLE IF NOT EXISTS `submission` (
    `id`	INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `pageid`	INT NOT NULL, -- pageid of the page on the target wiki
    `campaign_id`	INT(11) NOT NULL, -- campaign id
    `title`	TEXT NOT NULL, -- title of the page on the target wiki
    `oldid`	INT(11) NOT NULL, -- revision id of the page on the home wiki
    `target_wiki`	TEXT NOT NULL, -- target wiki language code
    `submitted_at`	TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- submission time
    `submitted_by_id`	INT(11) NOT NULL, -- user id of the submitter
    `submitted_by_username`	TEXT NOT NULL, -- username of the submitter
    `created_at`	TEXT NOT NULL, -- creation time of the page on the target wiki
    `created_by_id`	INT(11) NOT NULL, -- user id of the created_by
    `created_by_username`	TEXT NOT NULL, -- username of the created_by
    `total_bytes`	INT(11) NOT NULL, -- total bytes of the page on the target wiki
    `total_words`	INT(11)  NULL DEFAULT NULL, -- total words of the page on the target wiki
    `added_bytes`	INT(11)  NULL DEFAULT NULL, -- added bytes of the page on the target wiki
    `added_words`	INT(11)  NULL DEFAULT NULL, -- added words of the page on the target wiki
    `positive_votes`	INT(11) NOT NULL DEFAULT 0, -- positive votes of the submission
    `negative_votes`	INT(11) NOT NULL DEFAULT 0, -- negative votes of the submission
    `total_votes`	INT(11) NOT NULL DEFAULT 0, -- total votes of the submission
    `points`	INT(11) NOT NULL DEFAULT 0, -- points of the submission
    `judgable`	BOOLEAN NOT NULL DEFAULT TRUE, -- whether the submission is judgable
    `newly_created`	BOOLEAN NOT NULL DEFAULT FALSE, -- whether the submission is newly create
    CONSTRAINT `submission_newly_created_check` CHECK(NOT `newly_created` OR (`newly_created` AND `created_by_username` = `submitted_by_username` AND `created_by_id` = `submitted_by_id`)),
    CONSTRAINT `submission_campaign_id_fkey` FOREIGN KEY(`campaign_id`) REFERENCES `campaign`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `submission_submitted_by_id_fkey` FOREIGN KEY(`submitted_by_id`) REFERENCES `user`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    -- CONSTRAINT `submission_date_check` CHECK(`submitted_at` >= `created_at`),
    CONSTRAINT `submission_unique_campaign_id_pageid` UNIQUE(`campaign_id`, `pageid`)
);
CREATE INDEX IF NOT EXISTS `submission_campaign_id_index` ON `submission` (`campaign_id`);
CREATE INDEX IF NOT EXISTS `submission_submitted_by_id_index` ON `submission` (`submitted_by_id`);
CREATE TABLE IF NOT EXISTS `jury` (
    `user_id`	INT(11) NOT NULL, -- user id of the jury
    `username`    TEXT NOT NULL, -- username of the jury
    `campaign_id`	INT(11) NOT NULL, -- campaign id
    `created_at`	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- creation time of the jury
    `allowed`	BOOLEAN NOT NULL DEFAULT TRUE, -- whether the jury is allowed to vote
    `judged_count`	INT(11) NOT NULL DEFAULT 0, -- how many articles did this jury judged? (less or equal to submission count)
    `positive_votes`	INT(11) NOT NULL DEFAULT 0, -- how many articles did this jury voted positive?
    `negative_votes`	INT(11) NOT NULL DEFAULT 0, -- how many articles did this jury voted negative?
    `total_votes`	INT(11) NOT NULL DEFAULT 0, -- how many articles did this jury voted?
    `unevaluated_count` INT(11) NOT NULL DEFAULT 0, -- how many articles did this jury not evaluated yet?
    CONSTRAINT `jury_campaign_id_fkey` FOREIGN KEY(`campaign_id`) REFERENCES `campaign`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `jury_user_id_fkey` FOREIGN KEY(`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `PK_jury` PRIMARY KEY (`user_id`,`campaign_id`)
);
CREATE INDEX IF NOT EXISTS `jury_campaign_id_index` ON `jury` (`campaign_id`);
CREATE INDEX IF NOT EXISTS `jury_user_id_index` ON `jury` (`user_id`);
CREATE TABLE IF NOT EXISTS `jury_vote` (
    `jury_id`	INT(11) NOT NULL, -- user id of the jury
    `submission_id`	INT(11) NOT NULL, -- submission id
    `campaign_id` INT(11) NOT NULL, -- Campaign id
    `created_at`	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- creation time of the vote
    `vote`	INT(11) NOT NULL, -- vote value
    `note`	TEXT NULL DEFAULT NULL, -- note of the vote
    CONSTRAINT `PK_jury_vote` PRIMARY KEY (`jury_id`,`submission_id`),
    CONSTRAINT `jury_vote_submission_id_fkey` FOREIGN KEY(`submission_id`) REFERENCES `submission`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `jury_vote_campaign__user_id_fkey` FOREIGN KEY(`jury_id`,`campaign_id`) REFERENCES `jury`(`user_id`,`campaign_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `jury_vote_campaign_id_fkey` FOREIGN KEY(`campaign_id`) REFERENCES `campaign`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE INDEX IF NOT EXISTS `jury_vote_campaign_id_index` ON `jury_vote` (`campaign_id`);
CREATE INDEX IF NOT EXISTS `jury_vote_submission_id_index` ON `jury_vote` (`submission_id`);
CREATE INDEX IF NOT EXISTS `jury_vote_jury_id_index` ON `jury_vote` (`jury_id`);

CREATE TRIGGER IF NOT EXISTS
    `jury_post_insert_trigger`
AFTER INSERT ON `jury`
BEGIN
    -- Update jury evaluation count
    UPDATE
        `jury`
    SET
    `unevaluated_count` = (
        SELECT
            COUNT(*)
        FROM
            `submission`
        WHERE
            `submission`.`campaign_id` = NEW.`campaign_id`
        AND
            --- Not Already Voted
            `submission`.`id` NOT IN (
                SELECT
                    `jury_vote`.`submission_id`
                FROM
                    `jury_vote`
                WHERE
                    `jury_vote`.`jury_id` = NEW.`user_id`
                AND
                    `jury_vote`.`campaign_id` = NEW.`campaign_id`
            )
        AND
            --- Not his own submission
            `submission`.`submitted_by_id` != NEW.`user_id` 
    )
    WHERE
        `jury`.`campaign_id` = NEW.`campaign_id`
    AND
        `jury`.`user_id` = NEW.`user_id`;
END;




CREATE TRIGGER IF NOT EXISTS 
    `submission_post_trigger` 
AFTER INSERT ON `submission`
BEGIN
--- Update Campaign Statistics
   UPDATE `campaign`
        SET
            `total_submissions` = `total_submissions` + 1,  --- Increment the counter of the total number of articles submitted
            `total_newly_created` = `total_newly_created` + CAST(NEW.`created_by_id` = NEW.`submitted_by_id` AS  INT) --- Add a newly created submission
           --- `total_expanded` = `total_expanded` + CAST(NEW.`created_by_id` != NEW.`submitted_by_id` AS  INT)
    WHERE
        `campaign`.`id` = NEW.`campaign_id`;
--- Add a new submission to be evaluated by the jury
UPDATE
    `jury`
    SET
        `unevaluated_count` = `unevaluated_count` + 1
    WHERE
    --- All the jury of the campaign
        `jury`.`campaign_id` = NEW.`campaign_id`
    AND
    --- Not the submitter himself
        `jury`.`user_id` != NEW.`submitted_by_id`;
END;
CREATE TRIGGER IF NOT EXISTS 
    `submission_pre_delete_trigger` 
BEFORE DELETE ON `submission`
BEGIN
    --- Update Campaign Statistics
   UPDATE `campaign`
        SET
            `total_submissions` = `total_submissions` - 1,  --- Increment the counter of the total number of articles submitted
            `total_newly_created` = `total_newly_created` - CAST(OLD.`created_by_id` = OLD.`submitted_by_id` AS  INT) --- Add a newly created submission
           --- `total_expanded` = `total_expanded` - CAST(OLD.`created_by_id` != OLD.`submitted_by_id` AS  INT)
    WHERE
        `campaign`.`id` = OLD.`campaign_id`;
    --- Remove unevaluated_count for those who did not yet evaluated
    UPDATE `jury`
        SET 
            `unevaluated_count` = `unevaluated_count` - 1
        WHERE
            `jury`.`campaign_id` = OLD.`campaign_id`
        AND
        --- Those who did not yet evaluated
            `jury`.`user_id` NOT IN 
        (
            SELECT 
                `jury_vote`.`jury_id` 
            FROM
                `jury_vote`
            WHERE
                `jury_vote`.`submission_id` = OLD.`id`
        )
        AND
        --- Not the submitter himself
            `jury`.`user_id` != OLD.`submitted_by_id`;
END;

CREATE TRIGGER IF NOT EXISTS
    `jury_vote_pre_insert_trigger`
BEFORE INSERT ON `jury_vote`
BEGIN
    --- Check if the jury is also the submitter
    SELECT RAISE(ABORT, 'You cannot vote your own submission')
    WHERE NEW.`jury_id` = (
        SELECT `submitted_by_id` FROM `submission` WHERE `id` = NEW.`submission_id`
    );
    
END;


CREATE TRIGGER IF NOT EXISTS 
    `jury_vote_post_trigger` 
AFTER INSERT ON `jury_vote`
BEGIN
    --- Update Jury unevaluated and reduce the count
    UPDATE `jury`
    SET
        `unevaluated_count` = `unevaluated_count` - 1
    WHERE
        `jury`.`campaign_id` = NEW.`campaign_id`
    AND
        `jury`.`user_id` = NEW.`jury_id`;
    --- Recalculate the points of the submission
    UPDATE `submission`
        SET `points` = (
            SELECT
                CASE IFNULL(AVG(`vote`), 0)
                    WHEN 1 THEN 10
                    WHEN 0 THEN 0
                    ELSE 5
                END
            FROM `jury_vote`
            WHERE
                `jury_vote`.`submission_id` = NEW.`submission_id`
        ) WHERE `submission`.`id` = NEW.`submission_id`;
END;

CREATE TRIGGER IF NOT EXISTS 
    `jury_vote_post_update_trigger` 
AFTER UPDATE ON `jury_vote`
BEGIN
    --- Recalculate the points of the submission
    UPDATE `submission`
    SET `points` = (
        SELECT
                CASE IFNULL(AVG(`vote`), 0)
                    WHEN 1 THEN 10
                    WHEN 0 THEN 0
                    ELSE 5
                END
            FROM `jury_vote`
            WHERE
                `jury_vote`.`submission_id` = NEW.`submission_id`
    ) WHERE `submission`.`id` = NEW.`submission_id`;
END;
CREATE TRIGGER IF NOT EXISTS 
    `jury_vote_post_delete_trigger` 
AFTER DELETE ON `jury_vote`
BEGIN
    --- Recalculate the points of the submission
    UPDATE `submission`
        SET `points` = (
            SELECT
                CASE IFNULL(AVG(`vote`), 0)
                    WHEN 1 THEN 10
                    WHEN 0 THEN 0
                    ELSE 5
                END
            FROM `jury_vote`
            WHERE
                `jury_vote`.`submission_id` = OLD.`submission_id`
            )
        WHERE
            `submission`.`id` = OLD.`submission_id`;
END;



-- The Table would be used to store the statistics of a submission
CREATE TABLE IF NOT EXISTS `draft` (
    `id`	INT(11) NOT NULL PRIMARY KEY AUTOINCREMENT,
    `pageid`	INT(11) NOT NULL, -- pageid of the page on the target wiki
    `campaign_id`	INT(11) NOT NULL, -- campaign id
    `title`	TEXT NOT NULL, -- title of the page on the target wiki
    `oldid`	INT(11) NOT NULL, -- revision id of the page on the home wiki
    `target_wiki`	TEXT NOT NULL, -- target wiki language code
    `submitted_at`	TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- submission time
    `submitted_by_id`	INT(11) NOT NULL, -- user id of the submitter
    `submitted_by_username`	TEXT NOT NULL, -- username of the submitter
    `created_at`	TEXT NOT NULL, -- creation time of the page on the target wiki
    `created_by_id`	INT(11) NOT NULL, -- user id of the created_by
    `created_by_username`	TEXT NOT NULL, -- username of the created_by
    `total_bytes`	INT(11) NOT NULL, -- total bytes of the page on the target wiki
    `total_words`	INT(11)  NULL DEFAULT NULL, -- total words of the page on the target wiki
    `added_bytes`	INT(11)  NULL DEFAULT NULL, -- added bytes of the page on the target wiki
    `added_words`	INT(11)  NULL DEFAULT NULL, -- added words of the page on the target wiki
    `calculated`	BOOLEAN NOT NULL DEFAULT FALSE, -- whether the submission is calculated
    `passed`    BOOLEAN NOT NULL DEFAULT FALSE, -- whether the submission is passed
    `submitted`	BOOLEAN NOT NULL DEFAULT FALSE, -- whether the submission is submitted
    `newly_created`	BOOLEAN NOT NULL DEFAULT FALSE, -- whether the submission is newly created
    CONSTRAINT `draft_newly_created_check` CHECK(NOT `newly_created` OR (`newly_created` AND `created_by_username` = `submitted_by_username` AND `created_by_id` = `submitted_by_id`)),
    CONSTRAINT `criteria_campaign_id_fkey` FOREIGN KEY(`campaign_id`) REFERENCES `campaign`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `submission_submitted_by_id_fkey` FOREIGN KEY(`submitted_by_id`) REFERENCES `user`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
);




-- This Table would be used to store the topic 
CREATE TABLE IF NOT EXISTS `topic` (
    `id`	VARCHAR(100) NOT NULL PRIMARY KEY,
    `title`	VARCHAR(95) NOT NULL,
    `country`    VARCHAR(3) NOT NULL
);

-- This Table would be used to store the category
CREATE TABLE IF NOT EXISTS `category` (
    `id`	INT(11) NOT NULL PRIMARY KEY AUTOINCREMENT,
    `title`	TEXT NOT NULL UNIQUE
);

-- This Table would be used to store the task
CREATE TABLE IF NOT EXISTS `task` (
    `id`	INT(11) NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    `submitted_by` INT(11) NOT NULL,
    `status`	TEXT NOT NULL,
    `created_at`	TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `topic_id`	VARCHAR(100) NOT NULL,
    `task_data`	TEXT NOT NULL,
    `category_count`    INT(11) NOT NULL DEFAULT 0,
    `category_done`    INT(11) NOT NULL DEFAULT 0,
    `last_category`    TEXT NULL DEFAULT NULL,
    `target_wiki`    TEXT NOT NULL,
    `article_count`    INT(11) NOT NULL DEFAULT 0,
    `country`    TEXT NOT NULL,
    `pagepile_id`    INT(11) NULL DEFAULT NULL,
    FOREIGN KEY(`topic_id`) REFERENCES `topic`(`id`),
    FOREIGN KEY(`submitted_by`) REFERENCES `user`(`id`)
);
-- This Table would be used to store categories for a topic
CREATE TABLE IF NOT EXISTS `topic_category` (
    `topic_id`	VARCHAR(100) NOT NULL,
    `category_id`	INT(11) NOT NULL,
    PRIMARY KEY(`topic_id`,`category_id`)
);
COMMIT;
"""
conn = pymysql.connect(
    host="localhost",
    user="campwiz",
    password="password",
    database="campwiz"
)
conn.ping(reconnect=True)
cursor = conn.cursor()
statements = SQL1_INIT.split(";")
for statement in statements:
    if statement.strip() == "":
        continue
    cursor.execute(statement)
conn.commit()

SQL2_INIT = """
-- This Table would be used to store the article
CREATE TABLE IF NOT EXISTS `article` (
    `id`	INT(11) NOT NULL,
    `task_id`	INT(11) NOT NULL,
    `title`	TEXT NOT NULL,
    `target`	TEXT NOT NULL,
    `wikidata`	TEXT NULL DEFAULT NULL,
    `category`	TEXT NOT NULL,
    `created_at`	TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `target_lang` TEXT NULL DEFAULT NULL,
    PRIMARY KEY(`id`,`task_id`)
);
"""
SQL3_INIT = """
-- This Table would be used to store the system logs
CREATE TABLE IF NOT EXISTS `log` (
    `id`	INT(11) NOT NULL PRIMARY KEY AUTOINCREMENT,
    `created_at`	TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `level`	TEXT NOT NULL,
    `user_id`	INT(11) NULL DEFAULT NULL,
    `user_name`	TEXT NULL DEFAULT NULL,
    `message`	TEXT NOT NULL
);
"""
SQL3_LIST_LOGS_BY_ID = "SELECT * FROM `log` WHERE `id` > :id ORDER BY `id` DESC LIMIT :limit"
SQL3_LIST_LOGS_BY_USER_ID = "SELECT * FROM `log` WHERE `user_id` = :user_id ORDER BY `id` DESC LIMIT :limit"
SQL3_LIST_LOGS_BY_USER_NAME = "SELECT * FROM `log` WHERE `user_name` = :user_name ORDER BY `id` DESC LIMIT :limit"
SQL3_LIST_LOGS_BY_LEVEL = "SELECT * FROM `log` WHERE `level` = :level ORDER BY `id` DESC LIMIT :limit"
SQL3_LIST_LOGS_BY_LEVEL_AND_ID = "SELECT * FROM `log` WHERE `level` = :level AND `id` > :id ORDER BY `id` DESC LIMIT :limit"
SQL3_LIST_LOGS_BY_LEVEL_AND_USER_ID = "SELECT * FROM `log` WHERE `level` = :level AND `user_id` = :user_id ORDER BY `id` DESC LIMIT :limit"
SQL3_LIST_LOGS_BY_LEVEL_AND_USER_NAME = "SELECT * FROM `log` WHERE `level` = :level AND `user_name` = :user_name ORDER BY `id` DESC LIMIT :limit"
SQL3_LIST_LOGS_BY_LEVEL_AND_USER_ID_AND_ID = "SELECT * FROM `log` WHERE `level` = :level AND `user_id` = :user_id AND `id` > :id ORDER BY `id` DESC LIMIT :limit"
SQL3_GET_SINGLE_LOG_BY_ID = "SELECT * FROM `log` WHERE `id` = :id LIMIT 1"

SQL3_INSERT_LOG = """
INSERT INTO
    `log` (`level`, `user_id`, `user_name`, `message`)
VALUES
    (:level, :user_id, :username, :message);
"""
SQL1_CREATE_TASK = """
INSERT INTO
    `task` (status, topic_id, task_data, target_wiki, country, `category_count`, `submitted_by`)
VALUES
    (:status, :topic_id, :task_data, :target_wiki, :country, :category_count, :submitted_by);
"""
SQL1_GET_TASK = "SELECT * FROM `task` WHERE `id` = :task_id"
SQL1_GET_TASKS = "SELECT * FROM `task`"
SQL1_GET_TASKS_BY_STATUS = "SELECT * FROM `task` WHERE `status` = :status"

SQL2_GET_ARTICLES_BY_TASK_ID = "SELECT * FROM `article` WHERE `task_id` = :task_id ORDER BY `title` ASC"
SQL2_INSERT_ARTICLE = """
INSERT INTO
    `article` (`id`, `task_id`, `title`, target, wikidata, category, `target_lang`)
VALUES
    (:id, :task_id, :title, :target, :wikidata, :category, :target_lang)
    ON CONFLICT DO NOTHING;
"""
SQL2_GET_ARTICLE_BY_pageid_AND_TASK_ID = """
SELECT * FROM `article` WHERE `id` = :id AND `task_id` = :task_id;
"""

SQL1_INSERT_CATEGORY = """
INSERT INTO
    `category` (id, title)
VALUES
    (:id, :title)
    ON CONFLICT DO NOTHING;
"""
SQL1_INSERT_TOPIC_CATEGORY = """
INSERT INTO
    `topic_category` (topic_id, category_id)
VALUES
    (:topic_id, :category_id);
"""
SQL1_GET_CATEGORIES_BY_TOPIC_ID = """
SELECT
    `category`.`id` AS `id`,
    `category`.`title` AS `title`
FROM
    `category`
INNER JOIN
    `topic_category`
ON
    `category`.`id` = `topic_category`.`category_id`
WHERE
    `topic_category`.`topic_id` = :topic_id;
"""
SQL1_TASK_UPDATE_ARTICLE_COUNT = """
UPDATE
    `task` SET
        `article_count` = `article_count` + :new_added,
        `category_done` = `category_done` + :category_done,
        `last_category` = :last_category
WHERE `id` = :task_id
"""

SQL1_DELETE_UNUSED_ARTICLES = "DELETE FROM `article` WHERE `created_at` < CURRENT_TIMESTAMP - 60*60*24*7;"
SQL1_INSERT_TOPIC = "INSERT INTO `topic` (`id`, `title`, `country`) VALUES (:id, :title, :country);"
SQL1_GET_TOPIC_BY_ID = "SELECT * FROM `topic` WHERE `id` = :id;"
SQL1_GET_TOPICS = "SELECT * FROM `topic`;"

SQL1_GET_CATEGORY_BY_TOPIC_ID="""
SELECT
    `category`.`id` AS `id`,
    `category`.`title` AS `title`
FROM
    `category`
INNER JOIN
    `topic_category`
ON
    `category`.`id` = `topic_category`.`category_id`
WHERE
    `topic_category`.`topic_id` = :topic_id;
"""
SQL1_GET_CATEGORY_REL_BY_TOPIC_ID = """
SELECT
    `category_id` AS `id`
FROM
    `topic_category`
WHERE
    `topic_category`.`topic_id` = :topic_id;
"""
SQL1_INSERT_USER = "INSERT INTO `user` (`id`, `username`,`rights`, `wiki_registered_at`) VALUES (:id, :username, :rights, :wiki_registered_at)"
SQL1_GET_STATISTICS_FROM_USER="""
SELECT
    COUNT(*) AS `registered_user_count`,
    SUM(`article_count`) AS `total_articles`,
    SUM(`category_count`) AS `total_categories`,
    SUM(`task_count`) AS `total_tasks`
FROM `user`
    """
SQL1_UPDATE_TOPIC_CATEGORY_COUNT = """
UPDATE
    `topic` SET
        `category_count` = `category_count` + :category_count
WHERE `id` = :topic_id
"""
SQL1_DELETE_TOPIC_CATEGORY = """
DELETE FROM `topic_category` WHERE `topic_id` = :topic_id AND `category_id` = :category_id
"""
SQL1_GET_COUNTRIES = """
SELECT
    *
FROM
    `topic`
WHERE
    `id` LIKE :title_prefix
"""
SQL1_GET_USER_SUMMARY = """
SELECT
    *
FROM
    `user`
"""
SQL2_DELETE_UNUSED_ARTICLES = "DELETE FROM `article` WHERE `created_at` < ?"
SQL2_GET_MISSING_TRANSLATION = """
SELECT
    `article`.`id` AS `id`,
    `article`.`title` AS `title`,
    `article`.`target` AS `target`
FROM
    `article`
WHERE
    `task_id` = :task_id
"""
SQL1_INSERT_FEEDBACK = """
UPDATE
    `user` SET
        `feedback_ui_score` = :feedback_ui_score,
        `feedback_speed_score` = :feedback_speed_score,
        `feedback_note` = :feedback_note
WHERE `id` = :user_id
RETURNING *
"""
SQL1_GET_ALL_FEEDBACKS = """
SELECT
    `feedback_ui_score`,
    `feedback_speed_score`,
    `feedback_note`,
    `username`
FROM
    `user`
WHERE
    `feedback_ui_score` != 0
    OR `feedback_speed_score` != 0
    OR `feedback_note` != ''
ORDER BY `username` ASC
"""