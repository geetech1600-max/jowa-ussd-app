class Application:
    def __init__(self, db_connection):
        self.conn = db_connection

    def create(self, job_id, user_id):
        cur = self.conn.cursor()
        try:
            cur.execute("""
                INSERT INTO applications (job_id, user_id, status)
                VALUES (%s, %s, 'pending')
                ON CONFLICT (job_id, user_id) DO NOTHING
                RETURNING id, job_id, user_id, status, applied_at
            """, (job_id, user_id))
            
            application = cur.fetchone()
            self.conn.commit()
            
            if application:
                return {
                    'id': application[0],
                    'job_id': application[1],
                    'user_id': application[2],
                    'status': application[3],
                    'applied_at': application[4]
                }
            return None
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating application: {e}")
            return None
        finally:
            cur.close()

    def get_by_user_id(self, user_id, limit=10, offset=0):
        cur = self.conn.cursor()
        try:
            cur.execute("""
                SELECT a.id, j.title, e.company_name, a.status, a.applied_at
                FROM applications a
                JOIN jobs j ON a.job_id = j.id
                JOIN employers e ON j.employer_id = e.id
                WHERE a.user_id = %s
                ORDER BY a.applied_at DESC
                LIMIT %s OFFSET %s
            """, (user_id, limit, offset))
            
            applications = cur.fetchall()
            return [
                {
                    'id': app[0],
                    'job_title': app[1],
                    'company_name': app[2],
                    'status': app[3],
                    'applied_at': app[4]
                }
                for app in applications
            ]
        except Exception as e:
            print(f"Error getting user applications: {e}")
            return []
        finally:
            cur.close()

    def get_by_job_id(self, job_id):
        cur = self.conn.cursor()
        try:
            cur.execute("""
                SELECT a.id, u.full_name, u.phone_number, a.status, a.applied_at
                FROM applications a
                JOIN users u ON a.user_id = u.id
                WHERE a.job_id = %s
                ORDER BY a.applied_at DESC
            """, (job_id,))
            
            applications = cur.fetchall()
            return [
                {
                    'id': app[0],
                    'applicant_name': app[1],
                    'applicant_phone': app[2],
                    'status': app[3],
                    'applied_at': app[4]
                }
                for app in applications
            ]
        except Exception as e:
            print(f"Error getting job applications: {e}")
            return []
        finally:
            cur.close()