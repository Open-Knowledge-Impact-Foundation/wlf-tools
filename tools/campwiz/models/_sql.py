SQL1_SELECT_SUBMISSIONS = """
SELECT * FROM `submission` WHERE `campaign_id` = :campaign_id ORDER BY `id`
"""
SQL1_SELECT_SUBMISSIONS_EXCLUDING_USER_ID = """
SELECT * FROM `submission` WHERE `submission`.`campaign_id` = :campaign_id AND `id` NOT IN (
    SELECT `submission_id` FROM `jury_vote` WHERE  `jury_vote`.`jury_id` = :exclude_judged_user_id AND  `jury_vote`.`campaign_id` = :campaign_id
) AND `submitted_by_id` != :exclude_judged_user_id
ORDER BY `submission`.`id`
"""
SQL1_SELECT_SUBMISSIONS_JUDGED_BY_USER_ID = """
SELECT
    `s`.*, (`j`.`vote` * 10) AS `my_points`
FROM
    `submission` `s`
JOIN
    `jury_vote` `j` ON `j`.`submission_id` = `s`.`id`
WHERE
        `j`.`jury_id` = :jury_id
    AND
        `j`.`campaign_id` = :campaign_id
    AND
        `s`.`submitted_by_id` != :jury_id
ORDER BY `s`.`id`
"""


SQL1_SELECT_SUBMISSIONS_SUBMITTED_BY_USER_ID = """
SELECT * FROM `submission` WHERE `submitted_by_id` = :submitted_by_id AND `campaign_id` = :campaign_id
ORDER BY `submission`.`id`
"""
SQL1_CREATE_CAMPAIGN = """
INSERT INTO
    `campaign`
(
    --- `id`,
    `name`,
    `language`,
    `start_at`,
    `end_at`,
    `status`,
    `description`,
    `rules`,
    `blacklist`,
    `image`,
    `created_by_id`,
    `minimumAddedBytes`,
    `minimumAddedWords`,
    `minimumTotalBytes`,
    `minimumTotalWords`,
    `secretBallot`
)
VALUES
(
    --- :id,
    :name,
    :language,
    :start_at,
    :end_at,
    :status,
    :description,
    :rules,
    :blacklist,
    :image,
    :created_by_id,
    :minimumAddedBytes,
    :minimumAddedWords,
    :minimumTotalBytes,
    :minimumTotalWords,
    :secretBallot
) RETURNING *
"""
SQL1_GET_SUBMISSION_BY_ID = "SELECT * FROM `submission` WHERE `id` = :id LIMIT 1"
SQL1_GET_CAMPAIGN_BY_ID = "SELECT * FROM `campaign` WHERE `id` = :id"
SQL1_GET_USERS_BY_USERNAME_PREFIX = "SELECT * FROM `user` WHERE `username` IN "
SQL1_ADD_JURY_TO_CAMPAIGN = """
    INSERT INTO
        `jury` (`user_id`, `username`, `campaign_id`)
    VALUES
        (:user_id, :username, :campaign_id)
    ON CONFLICT DO UPDATE SET `allowed` = TRUE
"""
SQL1_REMOVE_JURY_FROM_CAMPAIGN = "DELETE FROM `jury` WHERE `user_id` = :user_id AND `campaign_id` = :campaign_id"
SQL1_GET_JURY_BY_ALLOWED = "SELECT * FROM `jury` WHERE `campaign_id` = :campaign_id AND `allowed` = :allowed"
SQL1_GET_JURY_BY_CAMPAIGN_ID = "SELECT * FROM `jury` WHERE `campaign_id` = :campaign_id"

SQL1_CREATE_USER_IF_NOT_EXISTS = """
INSERT OR IGNORE INTO
    `user` (
        `id`,
        `username`,
        `rights`,
        `wiki_registered_at`
    )
VALUES
(
    :id,
    :username,
    :rights,
    :wiki_registered_at
)
"""
SQL1_GET_ALL_CAMPAIGN = "SELECT * FROM `campaign` ORDER BY `id` DESC LIMIT :limit OFFSET :offset"
SQL1_GET_ALL_CAMPAIGN_BY_IDS_FORMAT = "SELECT * FROM `campaign` WHERE `id` IN ({id_placeholder}) ORDER BY `id` DESC"
SQL1_GET_ALL_CAMPAIGN_BY_LANGUAGE = "SELECT * FROM `campaign` WHERE `language` = :language ORDER BY `id` DESC LIMIT :limit OFFSET :offset"
SQL1_GET_ALL_CAMPAIGN_BY_STATUS_FORMAT = "SELECT * FROM `campaign` WHERE `status` IN ({status_placeholder}) ORDER BY `id` DESC LIMIT :limit OFFSET :offset"
SQL1_GET_ALL_CAMPAIGN_BY_STATUS_AND_LANGUAGE_FORMAT = "SELECT * FROM `campaign` WHERE `status` IN ({status_placeholder}) AND `language` = :language ORDER BY `id` DESC LIMIT :limit OFFSET :offset"

SQL1_UPDATE_CAMPAIGN_FORMAT = "UPDATE `campaign` SET {updates} WHERE `id` = {id} RETURNING *"
"""
id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `pageid`	INTEGER NOT NULL, -- pageid of the page on the target wiki
    `campaign_id`	INTEGER NOT NULL, -- campaign id
    `title`	TEXT NOT NULL, -- title of the page on the target wiki
    `oldid`	INTEGER NOT NULL, -- revision id of the page on the home wiki
    `target_wiki`	TEXT NOT NULL, -- target wiki language code
    `submitted_at`	TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- submission time
    `submitted_by_id`	INTEGER NOT NULL, -- user id of the submitter
    `submitted_by_username`	TEXT NOT NULL, -- username of the submitter
    `created_at`	TEXT NOT NULL, -- creation time of the page on the target wiki
    `created_by_id`	INTEGER NOT NULL, -- user id of the created_by
    `created_by_username`	TEXT NOT NULL, -- username of the created_by
    `total_bytes`	INTEGER NOT NULL, -- total bytes of the page on the target wiki
    `total_words`	INTEGER NOT NULL, -- total words of the page on the target wiki
    `added_bytes`	INTEGER NOT NULL, -- added bytes of the page on the target wiki
    `added_words`	INTEGER NOT NULL, -- added words of the page on the target wiki
"""

SQL1_CREATE_SUBMISSION = """
INSERT INTO
    `submission`
(
    `pageid`,
    `campaign_id`,
    `title`,
    `oldid`,
    `target_wiki`,
    `submitted_by_id`,
    `submitted_by_username`,
    `created_at`,
    `created_by_id`,
    `created_by_username`,
    `total_bytes`,
    `total_words`,
    `added_bytes`,
    `added_words`,
    `newly_created`
) VALUES (
    :pageid,
    :campaign_id,
    :title,
    :oldid,
    :target_wiki,
    :submitted_by_id,
    :submitted_by_username,
    :created_at,
    :created_by_id,
    :created_by_username,
    :total_bytes,
    :total_words,
    :added_bytes,
    :added_words,
    :newly_created
) RETURNING *
"""
SQL1_CREATE_LATE_SUBMISSION = """
INSERT INTO
    `submission`
(
    `pageid`,
    `campaign_id`,
    `title`,
    `oldid`,
    `target_wiki`,
    `submitted_by_id`,
    `submitted_by_username`,
    `created_at`,
    `created_by_id`,
    `created_by_username`,
    `total_bytes`,
    `total_words`,
    `added_bytes`,
    `added_words`,
    `newly_created`,
    `submitted_at`
) VALUES (
    :pageid,
    :campaign_id,
    :title,
    :oldid,
    :target_wiki,
    :submitted_by_id,
    :submitted_by_username,
    :created_at,
    :created_by_id,
    :created_by_username,
    :total_bytes,
    :total_words,
    :added_bytes,
    :added_words,
    :newly_created,
    :submitted_at
) RETURNING *
"""
SQL1_CREATE_DRAFT = """
INSERT INTO
    `draft`
(
    `pageid`,
    `campaign_id`,
    `title`,
    `oldid`,
    `target_wiki`,
    `submitted_by_id`,
    `submitted_by_username`,
    `created_at`,
    `created_by_id`,
    `created_by_username`,
    `total_bytes`,
    `total_words`,
    `added_bytes`,
    `added_words`,
    `newly_created`,
    `calculated`,
    `passed`
) VALUES (
    :pageid,
    :campaign_id,
    :title,
    :oldid,
    :target_wiki,
    :submitted_by_id,
    :submitted_by_username,
    :created_at,
    :created_by_id,
    :created_by_username,
    :total_bytes,
    :total_words,
    :added_bytes,
    :added_words,
    :newly_created,
    :calculated,
    :passed
) RETURNING *
"""
SQL1_GET_DRAFT_BY_ID = "SELECT * FROM `draft` WHERE `id` = :id LIMIT 1"
SQL1_UPDATE_DRAFT = """
UPDATE `draft` SET
    `calculated` = :calculated,
    `passed` = :passed,
    `submitted` = :submitted
WHERE `id` = :id
RETURNING *
"""
SQL1_ADD_JUDGEMENT = """
INSERT INTO
    `jury_vote`
(
    `submission_id`,
    `jury_id`,
    `vote`,
    `campaign_id`,
    `note`
) VALUES (
    :submission_id,
    :jury_id,
    :vote,
    :campaign_id,
    :note
) ON CONFLICT DO UPDATE SET `vote` = :vote, `note` = :note RETURNING *
"""
SQL1_GET_JUDGEMENTS_BY_SUBMISSION_ID = "SELECT `jury_vote`.*, `user`.`username` AS `judge_username` FROM `jury_vote` LEFT JOIN `user` ON `user`.`id`=`jury_vote`.`jury_id` WHERE `submission_id` = :submission_id"
SQL1_GET_JUDGEMENTS_BY_SUBMISSION_ID_AND_JUDGE_ID = "SELECT `jury_vote`.*, `user`.`username` AS `judge_username` FROM `jury_vote` LEFT JOIN `user` ON `user`.`id`=`jury_vote`.`jury_id` WHERE `submission_id` = :submission_id AND `jury_id` = :judge_id"
SQL1_GET_JURY_BY_SUBMISSION_ID = """
SELECT * FROM `jury` JOIN `jury_vote` ON `jury`.`user_id` = `jury_vote`.`jury_id` WHERE `jury_vote`.`submission_id` = :submission_id AND `jury`.`allowed` = TRUE
"""
SQL1_UPDATE_SUBMISSION_POINTS = """
UPDATE `submission` SET
    `positive_votes` = :positive_votes,
    `negative_votes` = :negative_votes,
    `total_votes` = :total_votes,
    `points` = :points
WHERE `id` = :id
RETURNING *  
"""
SQL1_VERIFY_JUDGE = "SELECT `allowed` FROM `jury` WHERE `user_id` = :user_id AND `campaign_id` = :campaign_id LIMIT 1"
SQL1_UPDATE_CAMPAIGN_STATUS = """
UPDATE
    `campaign`
    SET
        `status` = :status,
        `total_points` = IFNULL((
            SELECT
                SUM(`points`)
            FROM
                `submission`
            WHERE
                `campaign_id` = :id
        ), 0),
        `total_newly_created` = IFNULL((
            SELECT
                SUM(`newly_created`)
            FROM
                `submission`
            WHERE
                `campaign_id` = :id
        ), 0),
        `total_submissions` = IFNULL((
            SELECT
                COUNT(*)
            FROM
                `submission`
            WHERE
                `campaign_id` = :id
        ), 0),
        `total_new_users` = IFNULL((
            SELECT
                COUNT(DISTINCT `submitted_by_id`)
            FROM
                `submission`
            WHERE
                `campaign_id` = :id
        ), 0)
    WHERE `id` = :id RETURNING *
"""
SQL1_GET_RESULTS_BY_CAMPAIGN_ID = """
SELECT
    `submission`.`submitted_by_id` AS `user_id`,
    `submission`.`submitted_by_username` AS `username`,
    SUM(`submission`.`points`) AS `total_points`,
    SUM(`submission`.`newly_created`) AS `total_newly_created`,
    COUNT(*) AS `total_submissions`
FROM
    `submission`
WHERE
    `submission`.`campaign_id` = :campaign_id
GROUP BY
    `submission`.`submitted_by_id`
ORDER BY
    `total_points` DESC,
    `total_newly_created` DESC,
    `total_submissions` DESC;
"""
SQL1_UPDATE_CAMPAIGN_STATUS_TO_ENDED = """
-- Check if all jury has voted for all submissions of the campaign
SELECT
    MAX(`unevaluated_count`) AS `unjudged_submissions`
FROM
    `jury`
WHERE
    `jury`.`campaign_id` = :campaign_id
"""
SQL1_DELETE_SUBMISSION_BY_ID = "DELETE FROM `submission` WHERE `id` = :id"
SQL1_GET_SUBMISSION_TIMELINE_BY_LANGUAGE = """
SELECT
    DATE(`submission`.`submitted_at`) AS `date`,
    COUNT(*) AS `count`,
    (`submission`.`campaign_id` || '|' || (SELECT `name` FROM `campaign` WHERE `id` = `submission`.`campaign_id`)) AS `color`

FROM
    `submission`

GROUP BY
    DATE(`submission`.`submitted_at`), `submission`.`campaign_id`

ORDER BY
    `date` ASC
"""
SQL1_GET_SUBMISSION_TIMELINE_BY_SUBMITTED_BY_ID = """
SELECT
    DATE(`submission`.`submitted_at`) AS `date`,
    COUNT(*) AS `count`,
    SUM(`submission`.`points`) / 10 AS `points`,
    SUM(`submission`.`newly_created`) AS `newly_created`,
    `submission`.`submitted_by_username` AS `color`
FROM
    `submission`
WHERE
    `submission`.`campaign_id` = :campaign_id
GROUP BY
    DATE(`submission`.`submitted_at`), `submission`.`submitted_by_username`

ORDER BY
    DATE(`submission`.`submitted_at`) ASC
"""
SQL1_GET_NEW_SUBMISSIONS = """
SELECT
    `title`,
    `submitted_by_username`,
    `target_wiki`,
    `campaign_id`,
    `id`,
    `submitted_at`
FROM
    `submission`
WHERE
    `submission`.`submitted_at` > :last_update 
"""
SQL1_GET_NEW_EVALUATION = """
SELECT
    s.title AS title,
    s.target_wiki AS target_wiki,
    s.campaign_id AS campaign_id,
    s.submitted_by_username AS submitted_by_username,
    jv.*,
    u.username AS jury_username
FROM
    jury_vote jv
LEFT JOIN
    submission s
ON
    jv.submission_id = s.id
LEFT JOIN
    user u
ON
    jv.jury_id = u.id
WHERE
    jv.created_at > :last_update
"""
SQL1_NEXT_UNJUDGED_SUBMISSION = """
SELECT
    `submission`.`id` AS `id`
FROM
    `submission`
WHERE
    `submission`.`campaign_id` = :campaign_id
AND
    `submission`.`id` NOT IN (
        SELECT
            `jury_vote`.`submission_id`
        FROM
            `jury_vote`
        WHERE
            `jury_vote`.`jury_id` = :jury_id
        AND
            `jury_vote`.`campaign_id` = :campaign_id
    )
AND
    `submission`.`submitted_by_id` != :jury_id
ORDER BY
    `submission`.`id`
LIMIT 1
"""
