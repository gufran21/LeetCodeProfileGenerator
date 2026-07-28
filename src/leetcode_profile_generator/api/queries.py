"""GraphQL query strings for LeetCode's undocumented API.

All queries are reverse-engineered from LeetCode's frontend network traffic.
Isolating them here means schema changes only require updating this one file.

Endpoint: POST https://leetcode.com/graphql
Content-Type: application/json
"""

# Fetches user profile info + solved problem stats + beats percentages
QUERY_USER_PROFILE = """
query getUserProfile($username: String!) {
  matchedUser(username: $username) {
    username
    profile {
      realName
      ranking
      userAvatar
      aboutMe
    }
    submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
    problemsSolvedBeatsStats {
      difficulty
      percentage
    }
  }
  allQuestionsCount {
    difficulty
    count
  }
}
"""

# Fetches contest ranking summary + full contest history
QUERY_CONTEST_INFO = """
query getUserContestInfo($username: String!) {
  userContestRanking(username: $username) {
    attendedContestsCount
    rating
    globalRanking
    totalParticipants
    topPercentage
    badge {
      name
    }
  }
  userContestRankingHistory(username: $username) {
    attended
    contest {
      title
      startTime
    }
    rating
    ranking
    trendDirection
  }
}
"""

# Fetches submission calendar, streak, and active days for a specific year
QUERY_CALENDAR = """
query userProfileCalendar($username: String!, $year: Int) {
  matchedUser(username: $username) {
    userCalendar(year: $year) {
      activeYears
      streak
      totalActiveDays
      dccBadges {
        timestamp
        badge {
          name
          icon
        }
      }
      submissionCalendar
    }
  }
}
"""

# Fetches earned badges and upcoming badge progress
QUERY_BADGES = """
query userBadges($username: String!) {
  matchedUser(username: $username) {
    badges {
      id
      name
      shortName
      displayName
      icon
      hoverText
      creationDate
      category
      medal {
        slug
        config {
          iconGif
          iconGifBackground
        }
      }
    }
    upcomingBadges {
      name
      icon
      progress
    }
  }
}
"""

# Fetches recent accepted submissions
QUERY_RECENT_SUBMISSIONS = """
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    id
    title
    titleSlug
    timestamp
  }
}
"""
