export const ROLES = {
  EMPLOYEE: "EMPLOYEE",
  TEAM_LEAD: "TEAM_LEAD",
  MANAGER: "MANAGER",
  SENIOR_MANAGER: "SENIOR_MANAGER",
  DIRECTOR: "DIRECTOR",
  CEO: "CEO",
  HR_ASSOCIATE: "HR_ASSOCIATE",
  HR_EXECUTIVE: "HR_EXECUTIVE",
  HR_MANAGER: "HR_MANAGER",
  HR_DIRECTOR: "HR_DIRECTOR",
  ADMIN: "ADMIN",
};

export const APPROVER_ROLES = [
  ROLES.TEAM_LEAD,
  ROLES.MANAGER,
  ROLES.SENIOR_MANAGER,
  ROLES.DIRECTOR,
  ROLES.HR_MANAGER,
  ROLES.HR_DIRECTOR,
  ROLES.CEO,
];

export const HR_ROLES = [ROLES.HR_ASSOCIATE, ROLES.HR_EXECUTIVE, ROLES.HR_MANAGER, ROLES.HR_DIRECTOR];

export function isApprover(user) {
  return user && APPROVER_ROLES.includes(user.role);
}

export function isHr(user) {
  return user && HR_ROLES.includes(user.role);
}

export function isAdmin(user) {
  return user && user.is_admin;
}
