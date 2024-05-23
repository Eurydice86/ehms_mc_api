.mode column

with cte as
(select * from
presences p
join
members m
on p.member_id = m.member_id
join
events e
on p.event_id = e.event_id
join
groups g
on e.group_id = g.group_id
)
select count(*) from cte
where member_id like '786'
and group_name like 'Saksalainen miekkailu'
and confirmed like 'True';
