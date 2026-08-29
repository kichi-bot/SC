(function () {
  'use strict';

  var STORAGE_KEY = 'sc-pm-grader-desktop-v2';
  var TIMER_SECONDS = 75 * 60;
  var saveTimer = null;
  var timerHandle = null;
  var toastTimer = null;

  var PDF_BASE = '../IPA_SC_Mondai/2025_R07/%E7%A7%8B%E6%9C%9F/';
  var EXAM = {
    id: 'r7a',
    label: '令和7年度 秋期',
    period: '令和7年秋期',
    pdf: PDF_BASE + '2025r07a_sc_pm_qs.pdf',
    answerPdf: PDF_BASE + '2025r07a_sc_pm_ans.pdf',
    commentPdf: PDF_BASE + '2025r07a_sc_pm_cmnt.pdf',
    questions: [
      {
        id: 'q1',
        number: '問1',
        theme: 'WEB / 開発 / IR',
        title: 'コンサルティング業務で利用するSaaS',
        summary: 'ロール昇格と格納型XSSを追い、開発プロセスの対策まで考える。',
        pageStart: 2,
        pageEnd: 7,
        groups: [
          {
            title: '設問1',
            description: 'CSP設定時のスクリプト実行可否',
            fields: [
              field('q1-s1-a', 'a', 2, 'select', 'できない', {
                options: ['できる', 'できない'], accepted: ['できない']
              }),
              field('q1-s1-b', 'b', 2, 'select', 'できない', {
                options: ['できる', 'できない'], accepted: ['できない']
              })
            ]
          },
          {
            title: '設問2',
            description: '攻撃内容を図とスクリプトから読み取る',
            fields: [
              field('q1-s2-1', '(1)', 3, 'text', 'ロール管理', {
                accepted: ['ロール管理'], placeholder: '機能名を入力'
              }),
              field('q1-s2-c', '(2) c', 3, 'text', 'タスク名', {
                accepted: ['タスク名'], placeholder: '項目名を入力'
              }),
              field('q1-s2-d', '(3) d', 4, 'textarea', '個人タスク<script src="/files/F1234567890.xlsx"></script>', {
                accepted: ['個人タスク<script src="/files/F1234567890.xlsx"></script>'],
                placeholder: '入力された値を記述',
                rubric: [
                  rubric('タスク名', [['個人タスク']]),
                  rubric('script要素', [['script', 'src']]),
                  rubric('アップロード先', [['F1234567890.xlsx'], ['/files/']])
                ]
              }),
              field('q1-s2-e', '(4) e', 3, 'text', '管理者', {
                accepted: ['管理者'], placeholder: 'ロールを入力'
              }),
              field('q1-s2-f', '(4) f', 3, 'textarea', 'タスクの締切日を過ぎる。', {
                placeholder: '成立する条件を記述',
                rubric: [rubric('締切日', [['締切日'], ['期限']]), rubric('経過', [['過ぎ'], ['経過']])]
              }),
              field('q1-s2-g', '(4) g', 4, 'textarea', '利用者のロールを管理者に設定する。', {
                placeholder: '実行される処理を記述',
                rubric: [rubric('利用者のロール', [['利用者', 'ロール']]), rubric('管理者へ設定', [['管理者', '設定'], ['管理者', '変更']])]
              }),
              field('q1-s2-5', '(5)', 4, 'textarea', '図3のスクリプトをSサービス内にアップロードする工夫', {
                placeholder: 'CSPの制御を回避する工夫を記述',
                rubric: [rubric('スクリプト', [['スクリプト']]), rubric('Sサービス内', [['Sサービス', '内'], ['同一オリジン']]), rubric('アップロード', [['アップロード']])]
              })
            ]
          },
          {
            title: '設問3',
            description: 'ファイル検査とXSS対策',
            fields: [
              field('q1-s3-h', '(1) h', 5, 'textarea', 'アップロードされたファイルの形式が拡張子と整合しているかをチェックする。', {
                placeholder: '追加するチェック内容を記述',
                rubric: [rubric('ファイル形式', [['ファイル', '形式'], ['実体', '形式']]), rubric('拡張子', [['拡張子']]), rubric('整合性確認', [['整合'], ['一致']])]
              }),
              field('q1-s3-i', '(2) i', 4, 'text', 'プロジェクト進捗管理', {
                accepted: ['プロジェクト進捗管理'], placeholder: '機能名を入力'
              }),
              field('q1-s3-3', '(3)', 5, 'textarea', '出力時にエスケープ処理を施す。', {
                placeholder: '根本対策を記述',
                rubric: [rubric('出力時', [['出力時'], ['表示時']]), rubric('エスケープ', [['エスケープ'], ['無害化']])]
              })
            ]
          },
          {
            title: '設問4',
            description: '開発プロセスに追加する対策',
            fields: [
              field('q1-s4-j', 'j', 8, 'textarea', 'Sサービスの仕様を理解した専門家による脆弱性検査', {
                placeholder: '開発プロセスとしての対策を記述',
                rubric: [rubric('Sサービスの仕様', [['Sサービス', '仕様'], ['システム', '仕様']]), rubric('専門家', [['専門家'], ['有識者']]), rubric('脆弱性検査', [['脆弱性', '検査'], ['脆弱性診断']])]
              })
            ]
          }
        ]
      },
      {
        id: 'q2',
        number: '問2',
        theme: '暗号 / 鍵管理',
        title: '暗号資産交換業におけるセキュリティ',
        summary: '署名鍵の管理手順を追い、内部不正と暗号技術の使い分けを考える。',
        pageStart: 8,
        pageEnd: 14,
        groups: [
          {
            title: '設問1・2',
            description: '暗号処理とサイドチャネル攻撃',
            fields: [
              field('q2-s1', '設問1', 4, 'text', 'ウ，エ', {
                accepted: ['ウエ', 'エウ'], placeholder: '例：ウ、エ', hint: '二つ選択'
              }),
              field('q2-s2', '設問2', 5, 'textarea', '施設Kの外から，鍵管理PCの作動音や鍵管理PCから放出される電磁波を観測し，署名鍵Sを推測する。', {
                placeholder: '攻撃方法を具体的に記述',
                rubric: [rubric('施設Kの外', [['施設K', '外'], ['施設外']]), rubric('作動音又は電磁波', [['作動音'], ['電磁波']]), rubric('観測', [['観測'], ['測定']]), rubric('署名鍵Sの推測', [['署名鍵S', '推測'], ['署名鍵', '特定']])]
              })
            ]
          },
          {
            title: '設問3',
            description: '内部不正の手順と防止策',
            fields: [
              field('q2-s3-pos1', '(1) 挿入位置①', 2, 'text', '(i)と(ii)の間', {
                accepted: ['iとiiの間', '(i)と(ii)の間'], placeholder: '例：(i)と(ii)の間'
              }),
              field('q2-s3-act1', '(1) 追加する行為①', 4, 'textarea', 'Bコインを攻撃者に移転する移転情報を記録したファイルを業務用メディア内に追加する。', {
                placeholder: '追加される不正な行為を記述',
                rubric: [rubric('Bコインを攻撃者へ移転', [['Bコイン', '攻撃者', '移転']]), rubric('移転情報ファイル', [['移転情報', 'ファイル']]), rubric('業務用メディアへ追加', [['業務用メディア', '追加']])]
              }),
              field('q2-s3-pos2', '(1) 挿入位置②', 2, 'text', '(vi)と(vii)の間', {
                accepted: ['viとviiの間', '(vi)と(vii)の間'], placeholder: '例：(vi)と(vii)の間'
              }),
              field('q2-s3-act2', '(1) 追加する行為②', 4, 'textarea', 'Bコインを攻撃者に移転する署名済みの移転情報を記録したファイルを攻撃者に送信するとともに，業務用メディアから削除する。', {
                placeholder: '追加される不正な行為を記述',
                rubric: [rubric('署名済み移転情報', [['署名済み', '移転情報']]), rubric('攻撃者へ送信', [['攻撃者', '送信']]), rubric('メディアから削除', [['業務用メディア', '削除'], ['メディア', '消去']])]
              }),
              field('q2-s3-a', '(2) a', 3, 'text', 'メッセージ認証符号', {
                accepted: ['メッセージ認証符号', 'MAC'], placeholder: '暗号技術の名称を入力'
              }),
              field('q2-s3-3', '(3)', 4, 'textarea', '当日担当者を複数名とし，互いに確認しながら作業を実施するように手順を変更する。', {
                placeholder: '不正を防止する手順を記述',
                rubric: [rubric('複数名', [['複数名'], ['二人']]), rubric('相互確認', [['互いに確認'], ['相互確認'], ['ダブルチェック']]), rubric('作業手順', [['作業'], ['手順']])]
              })
            ]
          },
          {
            title: '設問4',
            description: '署名鍵の暗号化と分離管理',
            fields: [
              field('q2-s4-1', '(1)', 5, 'textarea', '作業2において，パスワードで暗号化した署名鍵Sと紙に書き留めたパスワードを一緒に移送している点', {
                placeholder: '問題のある運用を記述',
                rubric: [rubric('暗号化した署名鍵S', [['暗号化', '署名鍵S'], ['暗号化', '署名鍵']]), rubric('紙のパスワード', [['紙', 'パスワード']]), rubric('一緒に移送', [['一緒', '移送'], ['同時', '運搬']])]
              }),
              choiceField('q2-s4-b', '(2) b', 2, 'ウ'),
              choiceField('q2-s4-c', '(2) c', 2, 'ア'),
              choiceField('q2-s4-d', '(2) d', 2, 'エ'),
              choiceField('q2-s4-e', '(2) e', 2, 'ウ'),
              choiceField('q2-s4-a-jp', '(2) あ', 2, 'オ'),
              choiceField('q2-s4-i-jp', '(2) い', 2, 'ク'),
              field('q2-s4-3', '(3)', 3, 'textarea', '復号鍵Dがないので，暗号化された署名鍵Sは復号できない。', {
                placeholder: '復号できない理由を記述',
                rubric: [rubric('復号鍵Dがない', [['復号鍵D', 'ない'], ['復号鍵', '存在しない']]), rubric('署名鍵Sを復号できない', [['署名鍵S', '復号できない'], ['署名鍵', '復号不可']])]
              }),
              field('q2-s4-4', '(4)', 2, 'textarea', '攻撃者の生成した鍵ペアの暗号鍵', {
                placeholder: '暗号鍵を記述',
                rubric: [rubric('攻撃者が生成', [['攻撃者', '生成']]), rubric('鍵ペアの暗号鍵', [['鍵ペア', '暗号鍵']])]
              })
            ]
          }
        ]
      },
      {
        id: 'q3',
        number: '問3',
        theme: 'NW / ID / 認証',
        title: '情報システムのセキュリティ強化',
        summary: 'インターネットバンキングとVPN導入を題材に、接続前通信まで設計する。',
        pageStart: 15,
        pageEnd: 25,
        groups: [
          {
            title: '設問1・2',
            description: 'DNSと通信の保護、攻撃シナリオ',
            fields: [
              field('q3-s1-a', '設問1 (1) a', 4, 'text', 'DNSSEC', {
                accepted: ['DNSSEC'], placeholder: '技術名を入力'
              }),
              field('q3-s1-b', '設問1 (2) b', 4, 'text', 'DoH', {
                accepted: ['DoH', 'DNS over HTTPS'], placeholder: '技術名を入力'
              }),
              field('q3-s1-c', '設問1 (2) c', 4, 'text', 'TLS', {
                accepted: ['TLS'], placeholder: 'プロトコル名を入力'
              }),
              choiceField('q3-s2-d', '設問2 d', 4, 'イ'),
              choiceField('q3-s2-e', '設問2 e', 4, 'ア')
            ]
          },
          {
            title: '設問3・4',
            description: '接続元制限とVPN利用時の通信要件',
            fields: [
              field('q3-s3', '設問3', 6, 'textarea', 'Kサービス設定サイトへのアクセスが許可される接続元IPアドレスをa1.b1.c1.d1に制限する。', {
                placeholder: '具体的な設定内容を記述',
                rubric: [rubric('Kサービス設定サイト', [['Kサービス', '設定サイト']]), rubric('接続元IPアドレス', [['接続元IP']]), rubric('a1.b1.c1.d1に制限', [['a1.b1.c1.d1', '制限']])]
              }),
              field('q3-s4-f', '設問4 (1) f', 6, 'textarea', '各取引先サービスへの接続を許可するIPアドレスとして，P社専用のKサービス用固定グローバルIPアドレスを登録してもらう。', {
                placeholder: '取引先側に依頼する内容を記述',
                rubric: [rubric('各取引先サービス', [['取引先', 'サービス']]), rubric('P社専用', [['P社', '専用']]), rubric('固定グローバルIP', [['固定', 'グローバルIP']]), rubric('許可IPとして登録', [['許可', 'IP', '登録']])]
              }),
              field('q3-s4-2', '設問4 (2)', 7, 'textarea', 'Z-IB，OSベンダーのOSアップデート配布サイト，認証基盤サービス及びKサービス設定サイトへのHTTPSサービス', {
                placeholder: 'VPN接続前も含め、許可する通信を列挙',
                rubric: [rubric('Z-IB', [['Z-IB']]), rubric('OSアップデート配布サイト', [['OS', 'アップデート', '配布']]), rubric('認証基盤サービス', [['認証基盤']]), rubric('Kサービス設定サイト', [['Kサービス', '設定サイト']]), rubric('HTTPS', [['HTTPS']])]
              })
            ]
          },
          {
            title: '設問5',
            description: '認証の代替策とOS移行の運用',
            fields: [
              field('q3-s5-g', '(1) g', 4, 'textarea', '認証方式1の電話番号として，個人所有スマホの電話番号を登録する。', {
                placeholder: 'スマートフォン故障時の代替策を記述',
                rubric: [rubric('認証方式1の電話番号', [['認証方式1', '電話番号']]), rubric('個人所有スマホ', [['個人所有', 'スマホ'], ['個人', 'スマートフォン']]), rubric('登録', [['登録']])]
              }),
              field('q3-s5-2', '(2)', 7, 'textarea', 'Kサービス接続時のログからOSがバージョンXの社有PCを抽出し，アカウント名から利用者を特定後，利用者の所属する部の情報セキュリティ推進者に報告し，バージョンYへの移行を促してもらう。', {
                placeholder: 'ログを使った移行促進手順を記述',
                rubric: [rubric('接続ログ', [['Kサービス', 'ログ'], ['接続', 'ログ']]), rubric('バージョンXのPCを抽出', [['バージョンX', '抽出']]), rubric('アカウント名で利用者特定', [['アカウント名', '利用者', '特定']]), rubric('情報セキュリティ推進者へ報告', [['情報セキュリティ推進者', '報告']]), rubric('バージョンYへ移行', [['バージョンY', '移行']])]
              })
            ]
          }
        ]
      },
      {
        id: 'q4',
        number: '問4',
        theme: '委託 / OT / マルウェア',
        title: '製造業におけるセキュリティ管理',
        summary: 'SCADAを含む工場ネットワークで、権限・分離・復旧手順を設計する。',
        pageStart: 26,
        pageEnd: 35,
        groups: [
          {
            title: '設問1・2',
            description: 'リスク対応とアクセス権限',
            fields: [
              field('q4-s1-a', '設問1 a', 3, 'text', '未知の', {
                accepted: ['未知の', '未知'], placeholder: '字句を入力'
              }),
              field('q4-s1-b', '設問1 b', 3, 'text', '暗号化', {
                accepted: ['暗号化'], placeholder: '字句を入力'
              }),
              field('q4-s2-c', '設問2 (1) c', 3, 'select', '回避', {
                options: ['回避', '移転', '低減', '保有'], accepted: ['回避']
              }),
              field('q4-s2-d', '設問2 (1) d', 3, 'select', '移転', {
                options: ['回避', '移転', '低減', '保有'], accepted: ['移転']
              }),
              field('q4-s2-e', '設問2 (1) e', 3, 'select', '保有', {
                options: ['回避', '移転', '低減', '保有'], accepted: ['保有']
              }),
              {
                id: 'q4-s2-matrix',
                label: '設問2 (2) 権限マトリクス',
                type: 'matrix',
                points: 9,
                model: '総務課：×/×/×、情報システム課：×/×/○、営業部：○/○/×、設計課：○/×/×、製造課：○/×/×、品質保証課：○/×/×',
                rows: ['総務部総務課', '総務部情報システム課', '営業部', '製造部設計課', '製造部製造課', '製造部品質保証課'],
                columns: ['読込権限', '書込権限', '権限変更権限'],
                answer: [
                  ['×', '×', '×'],
                  ['×', '×', '○'],
                  ['○', '○', '×'],
                  ['○', '×', '×'],
                  ['○', '×', '×'],
                  ['○', '×', '×']
                ]
              }
            ]
          },
          {
            title: '設問3',
            description: 'USBメモリ経由のマルウェア対策',
            fields: [
              field('q4-s3-f', 'f', 5, 'textarea', '図3中の(け)の箇所に，追加でFW', {
                placeholder: '追加する機器と箇所を記述',
                rubric: [rubric('図3の(け)', [['(け)'], ['けの箇所']]), rubric('FWを追加', [['FW', '追加'], ['ファイアウォール', '追加']])]
              }),
              field('q4-s3-g', 'g', 5, 'textarea', 'USBメモリを接続したときの動きを確認するためのソフトウェアを導入した，社内LANから切り離された検査用PC', {
                placeholder: '検査用PCの要件を記述',
                rubric: [rubric('USBメモリの動作確認', [['USBメモリ', '動き', '確認'], ['USBメモリ', '挙動', '確認']]), rubric('確認用ソフトウェア', [['ソフトウェア', '導入']]), rubric('社内LANから分離', [['社内LAN', '切り離'], ['ネットワーク', '分離']]), rubric('検査用PC', [['検査用PC']])]
              })
            ]
          },
          {
            title: '設問4',
            description: '迅速な復旧とネットワーク分離',
            fields: [
              field('q4-s4-h', '(1) h', 4, 'textarea', 'SCADA内のNCプログラムをバックアップ／リストアするための媒体とソフトウェア', {
                placeholder: '平常時に準備するものを記述',
                rubric: [rubric('NCプログラム', [['NCプログラム']]), rubric('バックアップ／リストア', [['バックアップ', 'リストア'], ['バックアップ', '復元']]), rubric('媒体とソフトウェア', [['媒体', 'ソフトウェア']])]
              }),
              field('q4-s4-i', '(1) i', 4, 'textarea', 'SCADAにNCプログラムをリストアする手順', {
                placeholder: '平常時に整備する手順を記述',
                rubric: [rubric('SCADA', [['SCADA']]), rubric('NCプログラム', [['NCプログラム']]), rubric('リストア手順', [['リストア', '手順'], ['復元', '手順']])]
              }),
              field('q4-s4-j', '(2) j', 3, 'textarea', 'マルウェアに感染した一般PCが，正常な通信を妨害するパケットを大量に送信して，SCADAと工作機械の間の通信ができなくなる。', {
                placeholder: '想定する被害シナリオを記述',
                rubric: [rubric('感染した一般PC', [['感染', '一般PC']]), rubric('妨害パケットを大量送信', [['妨害', 'パケット', '大量'], ['DoS']]), rubric('SCADAと工作機械の通信不能', [['SCADA', '工作機械', '通信', 'できなく']])]
              }),
              field('q4-s4-k', '(2) k', 3, 'textarea', 'SCADA，工作機械及び製造監視用PCだけの独立したLANを構成するためのネットワーク機器', {
                placeholder: '平常時に準備する機器を記述',
                rubric: [rubric('対象3種', [['SCADA', '工作機械', '製造監視用PC']]), rubric('独立したLAN', [['独立', 'LAN'], ['分離', 'ネットワーク']]), rubric('ネットワーク機器', [['ネットワーク機器']])]
              }),
              field('q4-s4-l', '(2) l', 2, 'textarea', 'SCADA，工作機械及び製造監視用PCをL社のネットワークから切り離す手順', {
                placeholder: 'インシデント時の手順を記述',
                rubric: [rubric('対象3種', [['SCADA', '工作機械', '製造監視用PC']]), rubric('L社ネットワークから切離し', [['L社', 'ネットワーク', '切り離'], ['L社', 'ネットワーク', '分離']]), rubric('手順', [['手順']])]
              })
            ]
          }
        ]
      }
    ]
  };

  var EXAMS = [EXAM]
    .concat(window.SC_PAST_EXAMS || [])
    .concat(window.SC_LEGACY_EXAMS || []);
  var QUESTION_GUIDES = {
    'r7a-q1': {
      text: '権限昇格と格納型XSSがどの操作を起点に成立するかを、画面・スクリプト・CSP設定の順に追います。対策は、入力ファイルの実体確認、出力時のエスケープ、仕様を理解した専門家による検査という層に分けて整理すると答案がまとまります。',
      url: 'https://www.sc-siken.com/kakomon/07_aki/'
    },
    'r7a-q2': {
      text: '暗号化鍵と署名鍵の役割を混同せず、不正な移転情報がどこで作成・署名・持出しされるかを手順表に沿って確認します。媒体の受渡し、作業者の分離、署名対象の照合までを一つの攻撃経路として書くのがポイントです。',
      url: 'https://www.sc-siken.com/kakomon/07_aki/'
    },
    'r7a-q3': {
      text: '認証方式、接続元IPアドレス、端末の状態をログから時系列に並べ、不正接続が成立した条件を特定します。対策は、本人確認、ネットワーク制限、端末管理の三つの層で、攻撃経路をどこで遮断するかまで具体化します。',
      url: 'https://www.sc-siken.com/kakomon/07_aki/'
    },
    'r7a-q4': {
      text: 'USBメモリからのマルウェア侵入と、情報系ネットワークから制御系への波及を分けて考えます。SCADAの独立性、持込み媒体の隔離検査、復旧可能なバックアップという順で、可用性を損なわない対策を整理します。',
      url: 'https://www.sc-siken.com/kakomon/07_aki/'
    },
    'r7h-q1': {
      text: '委託先・再委託先まで含むサプライチェーン上の責任範囲を明確にし、脆弱性発見から通知、修正、再配布までの流れを追います。SBOMとCI/CDは、影響製品の特定と検査の自動化を早める仕組みとして説明します。',
      url: 'https://www.sc-siken.com/kakomon/07_haru/'
    },
    'r7h-q2': {
      text: 'CVSSは脆弱性の深刻度、EPSSは悪用される可能性の予測という違いを押さえます。公開情報、実際の攻撃兆候、認証の有無、検査結果を組み合わせ、修正の優先順位を業務影響まで含めて判断します。',
      url: 'https://www.sc-siken.com/kakomon/07_haru/'
    },
    'r7h-q3': {
      text: 'アクセスキーや証明書が端末内のどこに保存され、アプリからどのように利用されるかを追います。WebViewで開くURLの検証、証明書の信頼確認、サーバ側の認可を組み合わせて、不正アプリや改ざん通信への対策を示します。',
      url: 'https://www.sc-siken.com/kakomon/07_haru/'
    },
    'r7h-q4': {
      text: '管理台帳にない公開資産をDNS、WHOIS、外部スキャンなどから発見し、所有者と廃止可否を確認します。古いCNAMEや重大な脆弱性を放置しないよう、資産発見から是正確認までを継続的な運用として書きます。',
      url: 'https://www.sc-siken.com/kakomon/07_haru/'
    },
    'r6a-q1': {
      text: '複数のログを時系列で照合し、侵害端末、悪用アカウント、C2通信を特定します。証拠を残すためのアカウント無効化、IoCを使った横展開調査、RDP接続元制限、DLPによる持出し抑止までを一連の対応として整理します。',
      url: 'https://www.sc-siken.com/kakomon/06_aki/pm1.html'
    },
    'r6a-q2': {
      text: 'SPFは送信元IPアドレス、DKIMは署名によるメール内容、DMARCはFromドメインとの整合と受信側ポリシーを確認する仕組みです。メール基盤の移行前後で、どのDNSレコードと鍵を変更するかを対応付けます。',
      url: 'https://www.sc-siken.com/kakomon/06_aki/pm2.html'
    },
    'r6a-q3': {
      text: 'ログ中のSQLインジェクションと格納型XSSを区別し、埋め込まれたスクリプトがフォームを書き換えて情報を送信する流れを追います。アプリケーションログとアクセスログを突き合わせ、攻撃を受けた利用者と漏えい範囲を特定します。',
      url: 'https://www.sc-siken.com/kakomon/06_aki/pm3.html'
    },
    'r6a-q4': {
      text: 'セッション固定、HSTS、MIMEスニッフィング、APIの認可不備を、起きる事象と対策の組で整理します。利用者が操作できる対象と返却するデータ範囲をサーバ側で制限することが、答案の中心になります。',
      url: 'https://www.sc-siken.com/kakomon/06_aki/pm4.html'
    },
    'r6h-q1': {
      text: 'RESTのステートレス性を起点に、JWTのalg=none拒否、トークン主体と対象利用者の照合、更新項目の許可リスト化を確認します。総当たり攻撃へのロックアウトやLog4ShellへのWAF対策も、攻撃成立条件と対応付けます。',
      url: 'https://www.sc-siken.com/kakomon/06_haru/pm1.html'
    },
    'r6h-q2': {
      text: 'HTTP GETフラッドとDNSリフレクションの違いを、送信元偽装と増幅の有無から見分けます。検知しきい値の誤検知とのバランス、VPNの入口、CDNやネットワーク境界での遮断を段階的に整理します。',
      url: 'https://www.sc-siken.com/kakomon/06_haru/pm2.html'
    },
    'r6h-q3': {
      text: 'XSS、CSRF、IDOR、SSRFの攻撃経路を、ブラウザ、Webアプリ、クラウドメタデータサービスの順に追います。所有者確認、接続先URLの制限、IMDSv2のトークン利用により、どこで攻撃を止めるかを示します。',
      url: 'https://www.sc-siken.com/kakomon/06_haru/pm3.html'
    },
    'r6h-q4': {
      text: 'JavaプログラムとDBの権限、例外発生時の処理、ログ出力内容をコードに沿って確認します。秘密情報をログに残さず、SHA-2を用い、finallyや自動クローズで資源を確実に解放する理由まで押さえます。',
      url: 'https://www.sc-siken.com/kakomon/06_haru/pm4.html'
    },
    'r5a-q1': {
      text: '複数の投稿をコメント記号でつなぎ、一つの格納型XSSスクリプトとして動かす手口を追います。出力時のエスケープに加え、XHRと画像アップロードを利用したセッションIDの窃取、なりすましまでを関連付けます。',
      url: 'https://www.sc-siken.com/kakomon/05_aki/pm1.html'
    },
    'r5a-q2': {
      text: '偽アクセスポイントと偽サイトへの誘導を、証明書の発行者・サーバ名の検証で見破る流れを確認します。EAP-TLSの端末証明書、来客用ネットワークの分離、IPアドレスやDNSの制御を組み合わせます。',
      url: 'https://www.sc-siken.com/kakomon/05_aki/pm2.html'
    },
    'r5a-q3': {
      text: 'フィッシングで有効時間内のワンタイムパスワードを盗む流れと、コンテナ内の環境変数から秘密情報が漏れる流れを区別します。WebAuthnのオリジン検証と署名、管理されたコード署名を対策の根拠として整理します。',
      url: 'https://www.sc-siken.com/kakomon/05_aki/pm3.html'
    },
    'r5a-q4': {
      text: '脅威、脆弱性、発生事象、事業影響、対策を一つの因果関係としてつなぎます。リスク値は問題文の条件と整合させ、対策は抽象論ではなく、想定した攻撃経路を直接遮断する内容にします。',
      url: 'https://www.sc-siken.com/kakomon/05_aki/pm4.html'
    }
  };
  var state = loadState();

  document.addEventListener('DOMContentLoaded', init);

  function field(id, label, points, type, model, extra) {
    var base = { id: id, label: label, points: points, type: type, model: model };
    return Object.assign(base, extra || {});
  }

  function choiceField(id, label, points, answer) {
    return field(id, label, points, 'select', answer, {
      options: ['ア', 'イ', 'ウ', 'エ', 'オ', 'カ', 'キ', 'ク'],
      accepted: [answer]
    });
  }

  function rubric(label, variants) {
    return { label: label, variants: variants };
  }

  function init() {
    verifyQuestionTotals();
    applyTheme(state.theme);
    bindStaticControls();
    renderExamSelect();
    renderQuestionTabs();
    renderActiveQuestion();
    renderTimer();
  }

  function defaultState() {
    return {
      activeExam: 'r7a',
      activeQuestion: 'q1',
      answers: {},
      grades: {},
      theme: preferredTheme(),
      timer: { remaining: TIMER_SECONDS, running: false }
    };
  }

  function loadState() {
    var base = defaultState();
    try {
      var saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
      if (!saved) return base;
      var savedExam = findExam(saved.activeExam) ? saved.activeExam : base.activeExam;
      return {
        activeExam: savedExam,
        activeQuestion: findQuestionInExam(savedExam, saved.activeQuestion) ? saved.activeQuestion : base.activeQuestion,
        answers: saved.answers && typeof saved.answers === 'object' ? saved.answers : {},
        grades: saved.grades && typeof saved.grades === 'object' ? saved.grades : {},
        theme: saved.theme === 'dark' || saved.theme === 'light' ? saved.theme : base.theme,
        timer: saved.timer && typeof saved.timer.remaining === 'number' ? { remaining: saved.timer.remaining, running: false } : base.timer
      };
    } catch (error) {
      return base;
    }
  }

  function scheduleSave() {
    var indicator = document.getElementById('saveStatus');
    if (indicator) {
      indicator.classList.add('saving');
      indicator.lastChild.nodeValue = ' 保存中';
    }
    clearTimeout(saveTimer);
    saveTimer = setTimeout(function () {
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (error) {}
      if (indicator) {
        indicator.classList.remove('saving');
        indicator.lastChild.nodeValue = ' 保存済み';
      }
    }, 280);
  }

  function bindStaticControls() {
    document.getElementById('examSelect').addEventListener('change', function (event) {
      setActiveExam(event.target.value);
    });
    document.getElementById('timerToggle').addEventListener('click', toggleTimer);
    document.getElementById('timerReset').addEventListener('click', resetTimer);
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    document.getElementById('gradeButton').addEventListener('click', gradeActiveQuestion);
    document.getElementById('progressExport').addEventListener('click', exportPublicProgress);
    document.getElementById('pageJump').addEventListener('change', function (event) {
      var page = document.querySelector('[data-page="' + event.target.value + '"]');
      var scroller = document.getElementById('problemScroll');
      if (page) scroller.scrollTo({ top: page.offsetTop - 14, behavior: 'smooth' });
    });
  }

  function preferredTheme() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    var isDark = theme === 'dark';
    var toggle = document.getElementById('themeToggle');
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    if (!toggle) return;
    toggle.setAttribute('aria-pressed', String(isDark));
    toggle.setAttribute('aria-label', isDark ? 'ライトモードに切り替える' : 'ダークモードに切り替える');
    toggle.title = isDark ? '現在はダークモードです' : '現在はライトモードです';
  }

  function toggleTheme() {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    applyTheme(state.theme);
    scheduleSave();
    showToast(state.theme === 'dark' ? 'ダークモードに切り替えました。' : 'ライトモードに切り替えました。');
  }

  function verifyQuestionTotals() {
    EXAMS.forEach(function (exam) {
      exam.questions.forEach(function (question) {
        var total = flattenFields(question).reduce(function (sum, item) { return sum + item.points; }, 0);
        if (total !== 50) console.warn(exam.id + '-' + question.id + ' の学習用配点が50点ではありません:', total);
      });
    });
  }

  function findExam(id) {
    return EXAMS.find(function (exam) { return exam.id === id; });
  }

  function activeExam() {
    return findExam(state.activeExam) || EXAMS[0];
  }

  function findQuestionInExam(examId, questionId) {
    var exam = findExam(examId);
    return exam && exam.questions.find(function (question) { return question.id === questionId; });
  }

  function findQuestion(id) {
    return activeExam().questions.find(function (question) { return question.id === id; });
  }

  function activeQuestion() {
    return findQuestion(state.activeQuestion) || activeExam().questions[0];
  }

  function displayQuestionNumber(question) {
    return question.number.indexOf('午後') === 0 ? question.number : '午後 ' + question.number;
  }

  function questionKey(question) {
    return state.activeExam + '-' + question.id;
  }

  function questionGuide(question) {
    return QUESTION_GUIDES[questionKey(question)] || (question.guide ? {
      text: question.guide,
      url: question.dojoUrl || ''
    } : null);
  }

  function flattenFields(question) {
    return question.groups.reduce(function (all, group) { return all.concat(group.fields); }, []);
  }

  function renderExamSelect() {
    var select = document.getElementById('examSelect');
    select.textContent = '';
    EXAMS.forEach(function (exam) {
      var option = textEl('option', '', exam.label);
      option.value = exam.id;
      select.append(option);
    });
    select.value = state.activeExam;
  }

  function renderQuestionTabs() {
    var container = document.getElementById('questionTabs');
    container.textContent = '';
    container.style.setProperty('--question-count', activeExam().questions.length);
    activeExam().questions.forEach(function (question) {
      var isActive = question.id === state.activeQuestion;
      var tab = el('button', 'question-tab' + (isActive ? ' active' : ''));
      tab.type = 'button';
      tab.setAttribute('role', 'tab');
      tab.setAttribute('aria-selected', isActive ? 'true' : 'false');
      tab.append(textEl('span', '', question.number));
      tab.append(textEl('strong', '', question.title));
      tab.append(textEl('small', '', question.theme));
      tab.addEventListener('click', function () { setActiveQuestion(question.id); });
      container.append(tab);
    });
  }

  function setActiveExam(examId) {
    if (!findExam(examId) || state.activeExam === examId) return;
    state.activeExam = examId;
    state.activeQuestion = activeExam().questions[0].id;
    resetTimer(false);
    scheduleSave();
    renderQuestionTabs();
    renderActiveQuestion();
  }

  function setActiveQuestion(questionId) {
    if (!findQuestion(questionId) || state.activeQuestion === questionId) return;
    state.activeQuestion = questionId;
    resetTimer(false);
    scheduleSave();
    renderQuestionTabs();
    renderActiveQuestion();
  }

  function renderActiveQuestion() {
    var exam = activeExam();
    var question = activeQuestion();
    document.getElementById('periodLabel').textContent = exam.period;
    document.getElementById('questionContextTitle').textContent = displayQuestionNumber(question);
    document.getElementById('pdfTitle').textContent = question.number + ' ' + question.title;
    document.getElementById('answerTitle').textContent = question.number + 'の答案';
    document.getElementById('pdfPages').textContent = '問題冊子 ' + question.pageStart + '〜' + question.pageEnd + 'ページ';
    var questionPdf = question.pdf || exam.pdf;
    var answerPdf = question.answerPdf || exam.answerPdf;
    var commentPdf = question.commentPdf || exam.commentPdf;
    var pdfUrl = questionPdf + '#page=' + question.pageStart + '&zoom=page-width';
    document.getElementById('openPdfLink').href = pdfUrl;
    setResourceLink(document.getElementById('answerPdfLink'), answerPdf);
    setResourceLink(document.getElementById('commentPdfLink'), commentPdf);
    renderProblemPages(exam, question);
    renderAnswerForm(question);
    renderProgress(question);
    renderScoreSummary(question);
    document.getElementById('answerScroll').scrollTop = 0;
  }

  function renderProblemPages(exam, question) {
    var pages = document.getElementById('problemPages');
    var jump = document.getElementById('pageJump');
    pages.textContent = '';
    jump.textContent = '';
    for (var pageNo = question.pageStart; pageNo <= question.pageEnd; pageNo++) {
      var figure = el('figure', 'problem-page');
      figure.dataset.page = String(pageNo);
      var image = el('img');
      image.src = 'assets/sc_pm_pages/' + (question.assetId || exam.id) + '/page-' + String(pageNo).padStart(2, '0') + '.webp';
      image.alt = exam.period + ' ' + question.number + ' 問題冊子' + pageNo + 'ページ';
      image.loading = pageNo === question.pageStart ? 'eager' : 'lazy';
      image.decoding = 'async';
      figure.append(image, textEl('figcaption', '', pageNo + ' / ' + question.pageEnd));
      pages.append(figure);

      var option = textEl('option', '', 'ページ ' + pageNo);
      option.value = String(pageNo);
      jump.append(option);
    }
    jump.value = String(question.pageStart);
    document.getElementById('problemScroll').scrollTop = 0;
  }

  function setResourceLink(link, url) {
    link.hidden = !url;
    link.href = url || '#';
  }

  function renderAnswerForm(question) {
    var form = document.getElementById('answerForm');
    var isGraded = Boolean(state.grades[questionKey(question)]);
    form.textContent = '';
    question.groups.forEach(function (group) {
      var section = el('section', 'answer-group');
      section.append(textEl('h4', '', group.title));
      if (group.description) {
        var description = textEl('p', 'answer-group-description', group.description);
        description.hidden = !isGraded;
        section.append(description);
      }
      group.fields.forEach(function (item) {
        section.append(renderField(question, item));
      });
      form.append(section);
    });
    applyGradeVisuals(question);
  }

  function renderField(question, item) {
    var block = el('div', 'field-block');
    block.dataset.fieldId = item.id;
    var labelRow = el('div', 'field-label-row');
    var label = textEl('label', '', item.label);
    label.htmlFor = item.id;
    labelRow.append(label, textEl('span', 'points', item.points + '点'));
    block.append(labelRow);
    if (item.hint) block.append(textEl('p', 'field-hint', item.hint));

    if (item.type === 'matrix') {
      block.append(renderMatrix(question, item));
    } else {
      var control;
      if (item.type === 'select') {
        control = el('select', 'answer-control');
        var blank = textEl('option', '', '選択してください');
        blank.value = '';
        control.append(blank);
        item.options.forEach(function (optionValue) {
          var option = textEl('option', '', optionValue);
          option.value = optionValue;
          control.append(option);
        });
      } else if (item.type === 'textarea') {
        control = el('textarea', 'answer-control');
        control.rows = 3;
      } else {
        control = el('input', 'answer-control');
        control.type = 'text';
      }
      control.id = item.id;
      control.name = item.id;
      control.value = answerValue(question, item.id);
      if (item.placeholder) control.placeholder = item.placeholder;
      if (item.limit) control.maxLength = item.limit;
      control.addEventListener('input', function () {
        setAnswer(question, item.id, control.value);
        updateCharCount(block, control, item);
      });
      control.addEventListener('change', function () { setAnswer(question, item.id, control.value); });
      block.append(control);
      var meta = el('div', 'field-meta');
      if (item.type === 'textarea' || item.limit) meta.append(textEl('span', 'char-count', '0字'));
      block.append(meta);
      updateCharCount(block, control, item);
    }
    return block;
  }

  function renderMatrix(question, item) {
    var wrap = el('div', 'matrix-wrap');
    var table = el('table', 'permission-matrix');
    var thead = el('thead');
    var headerRow = el('tr');
    headerRow.append(textEl('th', '', '所属組織'));
    item.columns.forEach(function (column) { headerRow.append(textEl('th', '', column)); });
    thead.append(headerRow);
    table.append(thead);
    var tbody = el('tbody');
    var values = matrixValue(question, item);
    item.rows.forEach(function (rowName, rowIndex) {
      var row = el('tr');
      row.append(textEl('th', '', rowName));
      item.columns.forEach(function (column, columnIndex) {
        var cell = el('td');
        var select = el('select');
        select.setAttribute('aria-label', rowName + ' ' + column);
        ['', '○', '×'].forEach(function (symbol) {
          var option = textEl('option', '', symbol || '—');
          option.value = symbol;
          select.append(option);
        });
        select.value = values[rowIndex][columnIndex] || '';
        select.addEventListener('change', function () {
          var next = matrixValue(question, item);
          next[rowIndex][columnIndex] = select.value;
          setAnswer(question, item.id, next);
        });
        cell.append(select);
        row.append(cell);
      });
      tbody.append(row);
    });
    table.append(tbody);
    wrap.append(table);
    return wrap;
  }

  function answerValue(question, fieldId) {
    var key = questionKey(question);
    var questionAnswers = state.answers[key] || {};
    var value = questionAnswers[fieldId];
    return typeof value === 'string' ? value : '';
  }

  function matrixValue(question, item) {
    var key = questionKey(question);
    var existing = state.answers[key] && state.answers[key][item.id];
    if (Array.isArray(existing)) return existing.map(function (row) { return row.slice(); });
    return item.rows.map(function () { return item.columns.map(function () { return ''; }); });
  }

  function setAnswer(question, fieldId, value) {
    var key = questionKey(question);
    if (!state.answers[key]) state.answers[key] = {};
    state.answers[key][fieldId] = value;
    if (state.grades[key]) {
      delete state.grades[key];
      clearGradeVisuals();
      renderScoreSummary(activeQuestion());
    }
    scheduleSave();
    renderProgress(question);
    renderQuestionTabs();
  }

  function updateCharCount(block, control, item) {
    var counter = block.querySelector('.char-count');
    if (!counter) return;
    var count = Array.from(control.value).length;
    counter.textContent = item.limit ? count + ' / ' + item.limit + '字' : count + '字';
    counter.classList.toggle('over', Boolean(item.limit && count > item.limit));
  }

  function countAnswered(question) {
    var key = questionKey(question);
    return flattenFields(question).filter(function (item) {
      var value = state.answers[key] && state.answers[key][item.id];
      if (item.type === 'matrix') {
        return Array.isArray(value) && value.every(function (row) { return row.every(Boolean); });
      }
      return typeof value === 'string' && value.trim().length > 0;
    }).length;
  }

  function renderProgress(question) {
    if (!question || question.id !== state.activeQuestion) return;
    var fields = flattenFields(question);
    var answered = countAnswered(question);
    var percent = Math.round(answered / fields.length * 100);
    document.getElementById('answerProgressLabel').textContent = answered + ' / ' + fields.length + ' 入力';
    document.getElementById('answerProgressBar').style.width = percent + '%';
    document.getElementById('footerProgress').textContent = answered === fields.length ? 'すべて入力済み' : '未入力 ' + (fields.length - answered) + '問';
  }

  function gradeActiveQuestion() {
    var question = activeQuestion();
    var results = {};
    var total = 0;
    flattenFields(question).forEach(function (item) {
      var result = scoreField(question, item);
      results[item.id] = result;
      total += result.score;
    });
    state.grades[questionKey(question)] = {
      score: roundHalf(total),
      max: 50,
      results: results,
      gradedAt: new Date().toISOString()
    };
    scheduleSave();
    renderQuestionTabs();
    renderScoreSummary(question);
    applyGradeVisuals(question);
    document.getElementById('scoreSummary').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    showToast(question.number + 'を採点しました。模範解答と不足した観点を確認しましょう。');
  }

  function exportPublicProgress() {
    var questions = [];
    Object.keys(state.grades).forEach(function (key) {
      var grade = state.grades[key];
      if (!grade || typeof grade.score !== 'number' || typeof grade.max !== 'number' || !grade.gradedAt) return;
      var separator = key.indexOf('-');
      var exam = findExam(key.slice(0, separator));
      var question = exam && exam.questions.find(function (item) { return item.id === key.slice(separator + 1); });
      if (!exam || !question) return;
      questions.push({ exam: exam.period, question: question.number, score: grade.score, max: grade.max, gradedAt: grade.gradedAt });
    });
    questions.sort(function (a, b) { return String(a.gradedAt).localeCompare(String(b.gradedAt)); });
    var payload = { schemaVersion: 1, exportedAt: new Date().toISOString(), source: 'SC午後記述式セルフ採点', questions: questions };
    var blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = 'sc_pm_public_progress.json';
    link.click();
    URL.revokeObjectURL(url);
    showToast(questions.length + '問の公開用集計を保存しました。答案本文は含まれません。');
  }

  function scoreField(question, item) {
    var key = questionKey(question);
    var value = state.answers[key] && state.answers[key][item.id];
    if (item.type === 'matrix') return scoreMatrix(value, item);
    var normalized = normalize(value || '');
    if (!normalized) return resultObject(0, item.points, [], rubricLabels(item), true);

    var accepted = (item.accepted || []).map(normalize);
    var exact = accepted.some(function (answer) {
      return normalized === answer || (answer.length >= 3 && normalized.indexOf(answer) !== -1);
    });
    if (exact) return resultObject(item.points, item.points, rubricLabels(item), [], false);

    if (item.rubric && item.rubric.length) {
      var matched = [];
      var missing = [];
      item.rubric.forEach(function (criterion) {
        if (matchesCriterion(normalized, criterion)) matched.push(criterion.label);
        else missing.push(criterion.label);
      });
      var score = item.points * matched.length / item.rubric.length;
      return resultObject(roundHalf(score), item.points, matched, missing, false);
    }
    return resultObject(0, item.points, [], [], false);
  }

  function scoreMatrix(value, item) {
    var correct = 0;
    var filled = 0;
    var totalCells = item.rows.length * item.columns.length;
    if (Array.isArray(value)) {
      item.answer.forEach(function (row, rowIndex) {
        row.forEach(function (answer, columnIndex) {
          var user = value[rowIndex] && value[rowIndex][columnIndex];
          if (user) filled++;
          if (user === answer) correct++;
        });
      });
    }
    return {
      score: roundHalf(item.points * correct / totalCells),
      max: item.points,
      matched: [correct + ' / ' + totalCells + 'セル正解'],
      missing: correct === totalCells ? [] : [(totalCells - correct) + 'セルを見直す'],
      blank: filled === 0
    };
  }

  function matchesCriterion(normalizedValue, criterion) {
    return criterion.variants.some(function (variant) {
      return variant.every(function (term) { return normalizedValue.indexOf(normalize(term)) !== -1; });
    });
  }

  function resultObject(score, max, matched, missing, blank) {
    return { score: score, max: max, matched: matched, missing: missing, blank: blank };
  }

  function rubricLabels(item) {
    return (item.rubric || []).map(function (criterion) { return criterion.label; });
  }

  function normalize(value) {
    return String(value)
      .normalize('NFKC')
      .toLowerCase()
      .replace(/[\s\u3000、。，．,.・:：;；!！?？「」『』【】\[\]()（）<>＜＞\/／\\\-_—―]+/g, '');
  }

  function roundHalf(value) {
    return Math.round(value * 2) / 2;
  }

  function applyGradeVisuals(question) {
    clearGradeVisuals();
    var grade = state.grades[questionKey(question)];
    if (!grade) return;
    document.querySelectorAll('.answer-group-description').forEach(function (description) {
      description.hidden = false;
    });
    flattenFields(question).forEach(function (item) {
      var block = document.querySelector('[data-field-id="' + cssEscape(item.id) + '"]');
      var result = grade.results[item.id];
      if (!block || !result) return;
      var ratio = result.max ? result.score / result.max : 0;
      block.classList.add('graded');
      block.classList.add(ratio >= .99 ? 'is-correct' : ratio > 0 ? 'is-partial' : 'is-wrong');

      var resultBox = el('div', 'field-result');
      var resultLine = el('div', 'result-line');
      var badgeText = result.blank ? '未回答' : ratio >= .99 ? '要点OK' : ratio > 0 ? '部分点' : '要見直し';
      resultLine.append(textEl('span', 'result-badge', badgeText));
      resultLine.append(textEl('span', 'result-score', formatScore(result.score) + ' / ' + item.points + '点'));
      resultBox.append(resultLine);

      var model = el('p', 'model-answer');
      model.append(textEl('strong', '', '解答例　'));
      model.append(document.createTextNode(item.model));
      resultBox.append(model);
      var focus = rubricLabels(item);
      var explanation = el('p', 'answer-explanation');
      explanation.append(textEl('strong', '', '解説　'));
      explanation.append(document.createTextNode(focus.length
        ? '答案では「' + focus.join('・') + '」を問題文の根拠と対応させて書くのがポイントです。'
        : '問題文の条件と解答例を直接対応させ、用語だけでなく成立する理由も確認します。'));
      resultBox.append(explanation);
      if (result.missing && result.missing.length) {
        resultBox.append(textEl('p', 'rubric-note', '確認したい観点：' + result.missing.join(' / ')));
      }
      block.append(resultBox);
    });
  }

  function clearGradeVisuals() {
    document.querySelectorAll('.answer-group-description').forEach(function (description) {
      description.hidden = true;
    });
    document.querySelectorAll('.field-block.graded').forEach(function (block) {
      block.classList.remove('graded', 'is-correct', 'is-partial', 'is-wrong');
      var result = block.querySelector('.field-result');
      if (result) result.remove();
    });
  }

  function renderScoreSummary(question) {
    var container = document.getElementById('scoreSummary');
    var grade = state.grades[questionKey(question)];
    var currentScore = document.getElementById('currentScore');
    container.textContent = '';
    container.hidden = !grade;
    currentScore.textContent = grade ? formatScore(grade.score) + ' / 50点' : '未採点';
    currentScore.classList.toggle('scored', Boolean(grade));
    if (!grade) return;

    var grid = el('div', 'score-summary-grid');
    var ring = el('div', 'score-ring');
    ring.style.setProperty('--score-angle', (grade.score / 50 * 360) + 'deg');
    var ringScore = el('strong');
    ringScore.append(document.createTextNode(formatScore(grade.score)));
    ringScore.append(textEl('small', '', '/ 50点'));
    ring.append(ringScore);

    var copy = el('div');
    var headline = grade.score >= 35 ? '合格圏の答案です' : grade.score >= 25 ? 'あと一歩。抜けた観点を補強' : '模範解答から型を吸収しよう';
    copy.append(textEl('h4', '', headline));
    copy.append(textEl('p', '', 'これは独自の学習用採点です。意味が同じ別表現は、解答例を見て自分の答案にも点を加えてください。'));
    var actions = el('div', 'score-summary-actions');
    var printButton = textEl('button', '', '結果を印刷');
    printButton.type = 'button';
    printButton.addEventListener('click', function () { window.print(); });
    var topButton = textEl('button', '', '最初の設問へ');
    topButton.type = 'button';
    topButton.addEventListener('click', function () {
      var first = document.querySelector('.field-block');
      if (first) first.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    actions.append(printButton, topButton);
    copy.append(actions);
    grid.append(ring, copy);
    container.append(grid);

    var guide = questionGuide(question);
    if (guide) {
      var guideBox = el('section', 'question-guide');
      guideBox.append(textEl('h4', '', 'この問題の解説'));
      guideBox.append(textEl('p', '', guide.text));
      if (guide.url) {
        var hasDetailedPage = /\/pm\d+\.html$/.test(guide.url);
        var source = textEl('a', 'dojo-link', hasDetailedPage ? '過去問道場の詳しい解説を開く ↗' : '過去問道場の年度ページを開く ↗');
        source.href = guide.url;
        source.target = '_blank';
        source.rel = 'noopener';
        guideBox.append(source);
      }
      container.append(guideBox);
    }
  }

  function toggleTimer() {
    if (state.timer.remaining <= 0) state.timer.remaining = TIMER_SECONDS;
    state.timer.running = !state.timer.running;
    if (state.timer.running) {
      timerHandle = window.setInterval(function () {
        state.timer.remaining = Math.max(0, state.timer.remaining - 1);
        renderTimer();
        if (state.timer.remaining % 10 === 0) scheduleSave();
        if (state.timer.remaining === 0) {
          state.timer.running = false;
          clearInterval(timerHandle);
          timerHandle = null;
          showToast('75分が経過しました。いったん筆を止めて採点しましょう。');
        }
      }, 1000);
    } else {
      clearInterval(timerHandle);
      timerHandle = null;
      scheduleSave();
    }
    renderTimer();
  }

  function resetTimer(shouldSave) {
    clearInterval(timerHandle);
    timerHandle = null;
    state.timer = { remaining: TIMER_SECONDS, running: false };
    renderTimer();
    if (shouldSave !== false) scheduleSave();
  }

  function renderTimer() {
    var minutes = Math.floor(state.timer.remaining / 60);
    var seconds = state.timer.remaining % 60;
    var timer = document.getElementById('timer');
    if (!timer) return;
    timer.textContent = String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
    timer.classList.toggle('is-low', state.timer.remaining <= 10 * 60);
    document.getElementById('timerToggle').textContent = state.timer.running ? '停止' : state.timer.remaining === TIMER_SECONDS ? '開始' : '再開';
  }

  function showToast(message) {
    var toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.classList.remove('show'); }, 3600);
  }

  function formatScore(value) {
    return Number.isInteger(value) ? String(value) : value.toFixed(1);
  }

  function el(tag, className) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    return node;
  }

  function textEl(tag, className, text) {
    var node = el(tag, className);
    node.textContent = text;
    return node;
  }

  function cssEscape(value) {
    if (window.CSS && CSS.escape) return CSS.escape(value);
    return value.replace(/[^a-zA-Z0-9_-]/g, '\\$&');
  }
})();
