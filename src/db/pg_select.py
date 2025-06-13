from logging import error, info
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

class DbPool:
    def __init__(self):
        """
        连接PostgreSQL数据库
        返回连接池对象
        """
        try:
            connection_pool = pool.SimpleConnectionPool(
                1,  # 最小连接数
                100,  # 最大连接数
                host="47.106.71.193",
                database="beijia",
                user="ron", 
                password="ron3.14",
                port="5432"
            )
            if connection_pool:
                print("成功创建连接池")
            self.pool = connection_pool
        except Exception as error:
            print(f"创建连接池时发生错误: {error}")
            raise

    def select_data(self, table_name, columns="*", dict_flag=False, condition=None):
        try:
            conn = self.pool.getconn()
            if dict_flag==False:
                cursor = conn.cursor()
            else:
                cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = f"SELECT {columns} FROM {table_name}"
            if condition:
                query += f" WHERE {condition}"
            # print(f"--------{query}")
                
            cursor.execute(query)
            results = cursor.fetchall()
            # 释放连接
            self.pool.putconn(conn)
            
            return results
        except Exception as e:
            print(f"==select_data==failed: {e}")
            return None
    
    # 插入 users 库数据
    def ins_users(self, mobile, ver_code):
        max_retries = 10
        attempt = 0

        while attempt < max_retries:
            try:
                conn = self.pool.getconn()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO users (mobile, ver_code, exp_at)
                    VALUES (%s, %s, now() + interval '10 minutes')
                    ON CONFLICT (mobile) 
                    DO UPDATE SET 
                            ver_code = %s, 
                            exp_at = now() + interval '10 minutes',
                            is_ver = FALSE
                        WHERE users.exp_at < now()
                """, [mobile, ver_code, ver_code])

                # 提交事务
                conn.commit()
                affected_rows = cursor.rowcount
                info(f"==ins_users==success: {affected_rows}")

                return affected_rows
            except Exception as e:
                error(f"==ins_users==failed: {e}, retrying {attempt + 1}/{max_retries}")
                attempt += 1
                if attempt >= max_retries:
                    error("==ins_users==failed: Maximum retry attempts reached. Aborting.")
                    # raise SystemExit("==ins_agents==failed")
            finally:
                # 释放连接
                self.pool.putconn(conn)
    
    # 更新用户验证状态
    def update_user_verification(self, mobile):
        max_retries = 10
        attempt = 0

        while attempt < max_retries:
            try:
                conn = self.pool.getconn()
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE users 
                    SET is_ver = TRUE, updated_at = CURRENT_TIMESTAMP 
                    WHERE mobile = %s
                """, [mobile])

                # 提交事务
                conn.commit()
                affected_rows = cursor.rowcount
                info(f"==update_user_verification==success: {affected_rows}")

                return affected_rows
            except Exception as e:
                error(f"==update_user_verification==failed: {e}, retrying {attempt + 1}/{max_retries}")
                attempt += 1
                if attempt >= max_retries:
                    error("==update_user_verification==failed: Maximum retry attempts reached. Aborting.")
                    # raise SystemExit("==update_user_verification==failed")
            finally:
                # 释放连接
                self.pool.putconn(conn)
    # 插入 agents 库数据
    def ins_agents(self, agent_id, model, audio_model, name, description):
        max_retries = 10
        attempt = 0

        while attempt < max_retries:
            try:
                conn = self.pool.getconn()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO agents (agent_id, model, audio_model, name, description)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (agent_id) DO NOTHING
                """, [agent_id, model, audio_model, name, description])

                # 提交事务
                conn.commit()
                affected_rows = cursor.rowcount
                info(f"==ins_agents==success: {affected_rows}")

                return affected_rows
            except Exception as e:
                error(f"==ins_agents==failed: {e}, retrying {attempt + 1}/{max_retries}")
                attempt += 1
                if attempt >= max_retries:
                    error("==ins_agents==failed: Maximum retry attempts reached. Aborting.")
                    # raise SystemExit("==ins_agents==failed")
            finally:
                # 释放连接
                self.pool.putconn(conn)
    
    # 删除 agents 库数据
    async def del_agents(self, agents_id):
        max_retries = 10
        attempt = 0

        while attempt < max_retries:
            try:
                conn = self.pool.getconn()
                cursor = conn.cursor()

                cursor.execute("""
                    DELETE FROM agents 
                    WHERE agents_id=%s
                """, [agents_id, ])

                # 提交事务
                conn.commit()
                affected_rows = cursor.rowcount
                info(f"==del_agents==success: {affected_rows}")

                return affected_rows
            except Exception as e:
                error(f"==del_agents==failed: {e}, retrying {attempt + 1}/{max_retries}")
                attempt += 1
                if attempt >= max_retries:
                    error("==del_agents==failed: Maximum retry attempts reached. Aborting.")
                    # raise SystemExit("==del_agents==failed")
            finally:
                # 释放连接
                self.pool.putconn(conn)
    
    # 更新 agents 库数据
    async def update_agents(self, agents_id, model=None, name=None, description=None, audio_model=None):
        max_retries = 10
        attempt = 0

        while attempt < max_retries:
            try:
                conn = self.pool.getconn()
                cursor = conn.cursor()

                keys = []
                query = "UPDATE agents"
                if model!=None:
                    query += " model = %s"
                    keys.append(model)
                if name!=None:
                    query += " name = %s"
                    keys.append(name)
                if description!=None:
                    query += " description = %s"
                    keys.append(description)
                if audio_model!=None:
                    query += " audio_model = %s"
                    keys.append(audio_model)

                keys.append(agents_id)

                query += "updated_at=NOW() WHERE agents_id=%s"
                cursor.execute(query, keys)

                # 提交事务
                conn.commit()
                affected_rows = cursor.rowcount
                info(f"==update_agents==success: {affected_rows}")

                return affected_rows
            except Exception as e:
                error(f"==update_agents==failed: {e}, retrying {attempt + 1}/{max_retries}")
                attempt += 1
                if attempt >= max_retries:
                    error("==update_agents==failed: Maximum retry attempts reached. Aborting.")
                    # raise SystemExit("==update_agents==failed")
            finally:
                # 释放连接
                self.pool.putconn(conn)

    def convert_threads(self, threads):
        threads_dict = {}

        for i in threads:
            threads_dict[f'{i['agents_id']}__{i['user_id']}'] = i['threads_id']

        return threads_dict
    
    # 插入threads库数据
    def ins_threads(self, threads_id, agents_id, user_id):
        max_retries = 10
        attempt = 0

        while attempt < max_retries:
            try:
                conn = self.pool.getconn()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO threads (threads_id, agents_id, user_id)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (threads_id) DO NOTHING
                """, [threads_id, agents_id, user_id])

                # 提交事务
                conn.commit()
                affected_rows = cursor.rowcount
                info(f"==ins_threads==success: {affected_rows}")

                return affected_rows
            except Exception as e:
                error(f"==ins_threads==failed: {e}, retrying {attempt + 1}/{max_retries}")
                attempt += 1
                if attempt >= max_retries:
                    error("==ins_threads==failed: Maximum retry attempts reached. Aborting.")
                    # raise SystemExit("==ins_threads==failed")
            finally:
                # 释放连接
                self.pool.putconn(conn)
    
    # 插入 msgs 数据
    def ins_msgs(self, datas):
        max_retries = 10
        attempt = 0

        while attempt < max_retries:
            try:
                conn = self.pool.getconn()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO msgs (
                               thread_id, 
                               user_msg_id, user_text, user_audio, 
                               authentic_score, currect, currect_msgs, suggests, 
                               ai_msg_id, ai_text, ai_audio
                               )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_msg_id) DO NOTHING
                """, datas)

                # 提交事务
                conn.commit()
                affected_rows = cursor.rowcount
                info(f"==ins_msgs==success: {affected_rows}")

                return affected_rows
            except Exception as e:
                error(f"==ins_msgs==failed: {e}, retrying {attempt + 1}/{max_retries}")
                attempt += 1
                if attempt >= max_retries:
                    error("==ins_msgs==failed: Maximum retry attempts reached. Aborting.")
                    # raise SystemExit("==ins_msgs==failed")
            finally:
                # 释放连接
                self.pool.putconn(conn)

# 使用示例:
if __name__ == "__main__":
    db_pool = DbPool()

    if db_pool:
        # 查询所有数据
        # results = db_pool.select_data("threads", "threads_id, agents_id, user_id", True, None)
        # # print(len(results), results)
        # t = db_pool.convert_threads(results)
        # print(t)

        results = db_pool.select_data("msgs", "*", "true", f"thread_id='thread_9bcc4089-9ebc-4b0f-a1bc-c93ffe542c86' order by created_at desc limit 10")
        # results = db_pool.select_data("agents", "*", True, None)
        print(len(results), results)
# psql -h 47.106.71.193 -U ron -d beijia
