class Employer:
    def __init__(self, db_connection):
        self.conn = db_connection

    def create(self, phone_number, company_name, business_type):
        cur = self.conn.cursor()
        try:
            cur.execute("""
                INSERT INTO employers (phone_number, company_name, business_type) 
                VALUES (%s, %s, %s)
                ON CONFLICT (phone_number) DO UPDATE SET
                company_name = EXCLUDED.company_name,
                business_type = EXCLUDED.business_type
                RETURNING id, phone_number, company_name, business_type
            """, (phone_number, company_name, business_type))
            
            employer = cur.fetchone()
            self.conn.commit()
            
            if employer:
                return {
                    'id': employer[0],
                    'phone_number': employer[1],
                    'company_name': employer[2],
                    'business_type': employer[3]
                }
            return None
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating employer: {e}")
            return None
        finally:
            cur.close()

    def get_by_phone(self, phone_number):
        cur = self.conn.cursor()
        try:
            cur.execute("""
                SELECT id, phone_number, company_name, business_type, created_at
                FROM employers WHERE phone_number = %s
            """, (phone_number,))
            
            employer = cur.fetchone()
            if employer:
                return {
                    'id': employer[0],
                    'phone_number': employer[1],
                    'company_name': employer[2],
                    'business_type': employer[3],
                    'created_at': employer[4]
                }
            return None
        except Exception as e:
            print(f"Error getting employer: {e}")
            return None
        finally:
            cur.close()

    def get_employer_jobs(self, employer_id):
        cur = self.conn.cursor()
        try:
            cur.execute("""
                SELECT j.id, j.title, j.status, COUNT(a.id) as application_count
                FROM jobs j
                LEFT JOIN applications a ON j.id = a.job_id
                WHERE j.employer_id = %s
                GROUP BY j.id, j.title, j.status
                ORDER BY j.created_at DESC
                LIMIT 10
            """, (employer_id,))
            
            jobs = cur.fetchall()
            return [
                {
                    'id': job[0],
                    'title': job[1],
                    'status': job[2],
                    'application_count': job[3]
                }
                for job in jobs
            ]
        except Exception as e:
            print(f"Error getting employer jobs: {e}")
            return []
        finally:
            cur.close()