class Job:
    def __init__(self, db_connection):
        self.conn = db_connection

    def create(self, employer_id, title, description, location, payment_amount, payment_type):
        cur = self.conn.cursor()
        try:
            cur.execute("""
                INSERT INTO jobs (employer_id, title, description, location, payment_amount, payment_type)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, employer_id, title, description, location, payment_amount, payment_type, status
            """, (employer_id, title, description, location, payment_amount, payment_type))
            
            job = cur.fetchone()
            self.conn.commit()
            
            if job:
                return {
                    'id': job[0],
                    'employer_id': job[1],
                    'title': job[2],
                    'description': job[3],
                    'location': job[4],
                    'payment_amount': job[5],
                    'payment_type': job[6],
                    'status': job[7]
                }
            return None
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating job: {e}")
            return None
        finally:
            cur.close()

    def get_active_jobs(self, limit=10, offset=0):
        cur = self.conn.cursor()
        try:
            cur.execute("""
                SELECT j.id, j.title, j.location, j.payment_amount, j.payment_type, 
                       e.company_name, e.phone_number as employer_phone
                FROM jobs j
                JOIN employers e ON j.employer_id = e.id
                WHERE j.status = 'active'
                ORDER BY j.created_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            
            jobs = cur.fetchall()
            return [
                {
                    'id': job[0],
                    'title': job[1],
                    'location': job[2],
                    'payment_amount': job[3],
                    'payment_type': job[4],
                    'company_name': job[5],
                    'employer_phone': job[6]
                }
                for job in jobs
            ]
        except Exception as e:
            print(f"Error getting active jobs: {e}")
            return []
        finally:
            cur.close()

    def get_by_id(self, job_id):
        cur = self.conn.cursor()
        try:
            cur.execute("""
                SELECT j.id, j.title, j.description, j.location, j.payment_amount, j.payment_type,
                       e.company_name, e.phone_number as employer_phone
                FROM jobs j
                JOIN employers e ON j.employer_id = e.id
                WHERE j.id = %s
            """, (job_id,))
            
            job = cur.fetchone()
            if job:
                return {
                    'id': job[0],
                    'title': job[1],
                    'description': job[2],
                    'location': job[3],
                    'payment_amount': job[4],
                    'payment_type': job[5],
                    'company_name': job[6],
                    'employer_phone': job[7]
                }
            return None
        except Exception as e:
            print(f"Error getting job: {e}")
            return None
        finally:
            cur.close()