import sqlite3

class RoleManager:
    def __init__(self, db_name='roles.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS permissions (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS role_permissions (
                role_id INTEGER,
                permission_id INTEGER,
                FOREIGN KEY(role_id) REFERENCES roles(id),
                FOREIGN KEY(permission_id) REFERENCES permissions(id),
                UNIQUE(role_id, permission_id)
            )
        ''')
        self.conn.commit()

    def add_role(self, role_name):
        self.cursor.execute('INSERT INTO roles (name) VALUES (?)', (role_name,))
        self.conn.commit()

    def add_permission(self, permission_name):
        self.cursor.execute('INSERT INTO permissions (name) VALUES (?)', (permission_name,))
        self.conn.commit()

    def assign_permission_to_role(self, role_name, permission_name):
        self.cursor.execute('SELECT id FROM roles WHERE name = ?', (role_name,))
        role_id = self.cursor.fetchone()
        if not role_id:
            raise ValueError(f"Role '{role_name}' does not exist.")
        
        self.cursor.execute('SELECT id FROM permissions WHERE name = ?', (permission_name,))
        permission_id = self.cursor.fetchone()
        if not permission_id:
            raise ValueError(f"Permission '{permission_name}' does not exist.")
        
        self.cursor.execute('INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?)', (role_id[0], permission_id[0]))
        self.conn.commit()

    def check_permission(self, role_name, permission_name):
        self.cursor.execute('''
            SELECT 1 FROM role_permissions
            JOIN roles ON role_permissions.role_id = roles.id
            JOIN permissions ON role_permissions.permission_id = permissions.id
            WHERE roles.name = ? AND permissions.name = ?
        ''', (role_name, permission_name))
        return self.cursor.fetchone() is not None

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    manager = RoleManager()
    
    # Add roles
    manager.add_role('admin')
    manager.add_role('editor')
    manager.add_role('viewer')
    
    # Add permissions
    manager.add_permission('view_data')
    manager.add_permission('edit_data')
    manager.add_permission('delete_data')
    
    # Assign permissions to roles
    manager.assign_permission_to_role('admin', 'view_data')
    manager.assign_permission_to_role('admin', 'edit_data')
    manager.assign_permission_to_role('admin', 'delete_data')
    
    manager.assign_permission_to_role('editor', 'view_data')
    manager.assign_permission_to_role('editor', 'edit_data')
    
    manager.assign_permission_to_role('viewer', 'view_data')
    
    # Check permissions
    print(manager.check_permission('admin', 'delete_data'))  # True
    print(manager.check_permission('editor', 'delete_data')) # False
    print(manager.check_permission('viewer', 'edit_data'))   # False
    
    manager.close()