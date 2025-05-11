from fastapi import HTTPException, status
from sqlmodel import Session, select
from datetime import datetime

from ..logics import user_logic
from ..models.users import User, UserRole
from ..models.branches import BranchCreate, BranchUpdate, Branch

def create_branch(session: Session, cur_act_user: User, branch: BranchCreate) -> Branch:
    user_logic.require_role(cur_act_user, [UserRole.owner])
    
    branch_db = Branch.model_validate(branch)
    session.add(branch_db)
    session.commit()
    session.refresh(branch_db)
    return branch_db

def get_branches(session: Session, offset: int, limit: int) -> list[Branch]:
    branches_db = session.exec(select(Branch).offset(offset).limit(limit)).all()
    return branches_db

def get_branch_by_id(session: Session, branch_id: int) -> Branch:
    branch_db = session.get(Branch, branch_id)
    if not branch_db:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch_db

def update_branch_by_id(session: Session, cur_act_user: User, branch_id: int, branch: BranchUpdate) -> Branch:
    user_logic.require_role(cur_act_user, [UserRole.owner])

    branch_db = get_branch_by_id(session, branch_id)

    branch_data = branch.model_dump(exclude_unset=True)
    branch_db.sqlmodel_update(branch_data, update={"updated_at": datetime.now()})
    session.add(branch_db)
    session.commit()
    session.refresh(branch_db)
    return branch_db

def delete_branch_by_id(session: Session, cur_act_user: User, branch_id: int) -> dict[str, str]:
    user_logic.require_role(cur_act_user, [UserRole.owner])
    branch_db = get_branch_by_id(session, branch_id)

    session.delete(branch_db)
    session.commit()
    return {"msg": "Deleted branch successfully"}