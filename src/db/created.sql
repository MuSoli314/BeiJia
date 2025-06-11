-- 智能体表
-- DROP TABLE agents;
CREATE TABLE agents (
    agent_id VARCHAR(255) NOT NULL PRIMARY KEY,
    model VARCHAR(255) NOT NULL,
    audio_model VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 对话表
CREATE TABLE threads (
    threads_id VARCHAR(255) NOT NULL PRIMARY KEY,
    agents_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 消息表
-- DROP TABLE msgs;
CREATE TABLE IF NOT EXISTS msgs (
    thread_id VARCHAR(64) NOT NULL,
    user_msg_id VARCHAR(64) PRIMARY KEY,
    user_text TEXT,
    user_audio TEXT,
    authentic_score INTEGER CHECK (authentic_score >= 0),
    currect TEXT,
    currect_msgs TEXT[],
    suggests TEXT[],
    ai_msg_id VARCHAR(64),
    ai_text TEXT,
    ai_audio TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ron;
