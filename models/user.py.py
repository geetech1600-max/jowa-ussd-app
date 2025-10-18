class User:
    def __init__(self, db_connection):
        self.conn = db_connection

    def create(self, phone_number, full_name=None, skills=None, location=None):
        cur = self.conn.cursor()
        try:
            cur.execute("""
                INSERT INTO users (phone_number, full_name, skills, location) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (phone_number) DO UPDATE SET
                full_name = EXCLUDED.full_name,
                skills = EXCLUDED.skills,
                location = EXCLUDED.location
                RETURNING id, phone_number, full_name, skills, location
            """, (phone_number, full_name, skills, location))
            
            user = cur.fetchone()
            self.conn.commit()
            
            if user:
                return {
                    'id': user[0],
                    'phone_number': user[1],
                    'full_name': user[2],
                    'skills': user[3],
                    'location': user[4]
                }
            return None
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating user: {e}")
            return None
        finally:
            cur.close()

    def get_by_phone(self, phone_number):
        cur = self.conn.cursor()
        try:
            cur.execute("""
                SELECT id, phone_number, full_name, skills, location, created_at
                FROM users WHERE phone_number = %s
            """, (phone_number,))
            
            user = cur.fetchone()
            if user:
                return {
                    'id': user[0],
                    'phone_number': user[1],
                    'full_name': user[2],
                    'skills': user[3],
                    'location': user[4],
                    'created_at': user[5]
                }
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            cur.close()

    def update_profile(self, phone_number, full_name, skills, location):
        cur = self.conn.cursor()
        try:
            cur.execute("""
                UPDATE users 
                SET full_name = %s, skills = %s, location = %s
                WHERE phone_number = %s
                RETURNING id, phone_number, full_name, skills, location
            """, (full_name, skills, location, phone_number))
            
            user = cur.fetchone()
            self.conn.commit()
            
            if user:
                return {
                    'id': user[0],
                    'phone_number': user[1],
                    'full_name': user[2],
                    'skills': user[3],
                    'location': user[4]
                }
            return None
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating user: {e}")
            return None
        finally:
            cur.close()