import fetch from "node-fetch";
import { load } from "cheerio";
import fs from "fs";


const GROUP_ID1 = "REDACTED";
const GROUP_ID2 = "REDACTED";

async function fetchGroupHTML(groupId) {
  const res = await fetch(
    `https://vjudge.net/group/${groupId}`,
    {
      headers: {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://vjudge.net/"
      }
    }
  );

  if (res.status === 404) {
    throw new Error("❌ 404 — Not group member or not logged in");
  }

  return await res.text();
}

async function extractMembers(html) {
  const $ = load(html);
  const textarea = $('textarea[name="dataJson"]').text();

  if (!textarea) {
    throw new Error("❌ dataJson not found");
  }

  const data = JSON.parse(textarea);
  return data.memberBriefs;
}

async function getContests(html) {
  const $ = load(html);
  const textarea = $('textarea[name="dataJson"]').text();

  if (!textarea) {
    throw new Error("❌ dataJson not found");
  }

  const data = JSON.parse(textarea);

  return data.contests.map(c => ({
    id: c[0],
    name: c[1]
  }));
}


let rawstr = "";
let contestSolvedMaps = {};
async function fetchContestSolvedMap(contest) {
  const res = await fetch(
    `https://vjudge.net/contest/rank/single/${contest.id}`,
    { headers: { "User-Agent": "Mozilla/5.0" } }
  );
  const json = await res.json();
  rawstr += JSON.stringify(json) + "\n";
  // console.log(json);

  let maxIndex = -1;
  let scores = {}
  for (const sub of json.submissions) {

    const memberId = sub[0];
    const problemIndex = sub[1];
    const verdict = sub[2];
    const submit_time = sub[3];
    const score = sub[4];
    const fullScore = sub[5];

    if (submit_time >= json.length / 1000) continue;

    scores[memberId] ??= {};
    scores[memberId][problemIndex] ??= {
    score: 0,
    verdict: undefined
    };

    if (scores[memberId][problemIndex]['verdict'] !== 1) {
        if (verdict === 1) {
            scores[memberId][problemIndex]['score'] = 1
            scores[memberId][problemIndex]['verdict'] = verdict;
        } else {
            if (score !== undefined && fullScore !== undefined) {
                if (score / fullScore > scores[memberId][problemIndex]['score']) {
                    scores[memberId][problemIndex]['score'] = score / fullScore;
                    scores[memberId][problemIndex]['verdict'] = verdict;
                }
            } else {
                scores[memberId][problemIndex]['score'] = 0;
                scores[memberId][problemIndex]['verdict'] = verdict;
            }
        }
    }
    

    if (problemIndex > maxIndex) {
      maxIndex = problemIndex;
    }
  }
  maxIndex += 1;

  let totalScore = {}
  for (const m in scores) {
    totalScore[m] = 0;
    for (const p in scores[m]) {
        totalScore[m] += scores[m][p]['score'];
    }
    
    totalScore[m] = totalScore[m] / maxIndex;
  }

  let convertedKey = contestSolvedMaps[contest.name] !== undefined ? contestSolvedMaps[contest.name] : {};

  for (const k in totalScore) {
    convertedKey[json.participants[k][0]] = totalScore[k] * 10;
  }  

  return convertedKey;
}

(async () => {
  try {
    const html1 = await fetchGroupHTML(GROUP_ID1);
    let members1 = await extractMembers(html1);
    let contests1 = await getContests(html1);

    const html2 = await fetchGroupHTML(GROUP_ID2);
    let members2 = await extractMembers(html2);
    let contests2 = await getContests(html2);
    // console.log(contests2);

    const members = [...members1, ...members2];
    const contests = [...contests1, ...contests2];

    //console.log(contests);

    for (const contest of contests) {
        contestSolvedMaps[contest.name] = await fetchContestSolvedMap(contest);
    }

    // console.log(members.length);
    // console.log(contestSolvedMaps);
    fs.writeFileSync("rawfile.json", rawstr, "utf8");

    console.log("👥 Members:");

    let outputJson = {};

    const output = members
        .map(m => {
            const row = {
                member: extract10DigitId(m),
            };

            for (const contest of contests) {
                outputJson[row.member] ??= {};

                const solved = contestSolvedMaps[contest.name][m.username] ?? 0;
                outputJson[row.member][contest.name] = solved;
                row[contest.name] = solved;
            }

            return row;
        })
        .sort((a, b) => a.member.localeCompare(b.member)); // 🔤 alphabet sort

    // console.table(output);

    const jsonStr = JSON.stringify(outputJson, null, 2); // pretty print with 2 spaces

    // Write to file synchronously
    fs.writeFileSync('output.json', jsonStr, 'utf8');

    // Or asynchronously
    fs.writeFile('output.json', jsonStr, 'utf8', (err) => {
        if (err) throw err;
        console.log('JSON file saved!');
    });
    

  } catch (err) {
    console.error(err.message);
  }
})();

function extract10DigitId(member) {
  const regex = "\\d{10}";

  if (member.nickName) {
    const match = member.nickName.match(regex);
    if (match) return match[0];
  }

  if (member.username) {
    const match = member.username.match(regex);
    if (match) return match[0];
    return member.username;
  }

  return "";
}