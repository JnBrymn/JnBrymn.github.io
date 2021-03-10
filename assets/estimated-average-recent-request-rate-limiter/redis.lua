-- parameters and state
local lambda = 0.06931471805599453 -- 10 seconds half-life
local rate_limit = 0.5
local time_array = redis.call("time")
local now = time_array[1]+0.000001*time_array[2] -- seconds + microseconds
local Nkey = KEYS[1]..":N"
local Tkey = KEYS[1]..":T"

local N = redis.call("get", Nkey)
if N == false then
  N = 0
end

local T = redis.call("get", Tkey)
if T == false then
  T = 0
end

local delta_t = T-now

-- functions
local function evaluate()
  return N*lambda*math.exp(lambda*delta_t)
end

local function update()
  redis.call("set", Nkey, 1+N*math.exp(lambda*delta_t))
  redis.call("set", Tkey, now)
end

local function rate_limited()
  local estimated_rate = evaluate()
  local limited = estimated_rate > rate_limit
  update()
  return {limited, tostring(estimated_rate)}
end

-- the whole big show
return rate_limited()
