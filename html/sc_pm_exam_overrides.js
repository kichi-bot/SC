// 自動抽出データでは大問単位になっている設問を、実際の解答欄単位に補正する。
(function () {
  'use strict';

  var exams = window.SC_LEGACY_EXAMS || [];
  var exam = exams.find(function (item) { return item.id === 'r4a'; });
  var question = exam && exam.questions.find(function (item) { return item.id === 'pm2q2'; });
  if (!question) return;

  function criterion(label, variants) {
    return { label: label, variants: variants };
  }

  function answerField(id, label, points, model, options) {
    var settings = options || {};
    return {
      id: id,
      label: label,
      points: points,
      type: settings.type || 'text',
      model: model,
      accepted: settings.accepted || [model],
      placeholder: settings.placeholder || '解答を入力',
      hint: settings.hint || '',
      limit: settings.limit,
      rubric: settings.rubric || [criterion(model, [[model]])]
    };
  }

  question.answerFieldSchemaVersion = 2;
  question.groups = [
    {
      title: '設問1　マルウェアαの検知',
      description: '下線①・②を検知する単純ルールを、それぞれ問題文の条件と対応させます。',
      fields: [
        answerField('r4a-pm2q2-s1', '下線①（ファイル操作）', 5, 'メールフォルダ内のファイルが読み込まれた。', {
          type: 'textarea',
          limit: 30,
          placeholder: '30字以内で入力',
          rubric: [
            criterion('メールフォルダ', [['メールフォルダ']]),
            criterion('ファイルの読込み', [['ファイル', '読み込']])
          ]
        }),
        answerField('r4a-pm2q2-s2', '下線②（ネットワーク動作）', 4, 'HTTPでファイルがアップロードされた。', {
          type: 'textarea',
          limit: 30,
          placeholder: '30字以内で入力',
          rubric: [
            criterion('HTTP', [['HTTP']]),
            criterion('ファイルのアップロード', [['ファイル', 'アップロード']])
          ]
        })
      ]
    },
    {
      title: '設問2　マルウェアβの検知',
      description: '表5の空欄a〜eと、削除対象のファイルを問う(2)を別々に確認します。',
      fields: [
        answerField('r4a-pm2q2-s3', '(1) a（時刻）', 1, '15:03'),
        answerField('r4a-pm2q2-s4', '(1) b（PC名）', 1, 'PC1'),
        answerField('r4a-pm2q2-s5', '(1) c（ファイル名）', 1, 'file1.v'),
        answerField('r4a-pm2q2-s6', '(1) d（ファイル名）', 1, 'file2.v'),
        answerField('r4a-pm2q2-s7', '(1) e（PC名）', 1, 'PC2'),
        answerField('r4a-pm2q2-s8', '(2) 削除すべきファイル（記号を全て）', 4, 'ア、ウ、エ、オ、キ', {
          placeholder: '例：ア、ウ',
          rubric: [
            criterion('ア', [['ア']]),
            criterion('ウ', [['ウ']]),
            criterion('エ', [['エ']]),
            criterion('オ', [['オ']]),
            criterion('キ', [['キ']])
          ]
        })
      ]
    },
    {
      title: '設問3　検知ルールの作成',
      description: '下線④と同じ手順による感染拡大を検知する条件を整理します。',
      fields: [
        answerField('r4a-pm2q2-s9', '下線④の検知ルール', 8, 'Vソフトのデータファイルが読み込まれた後に、1分以内に、パス名が同一のファイルが上書きされた。', {
          type: 'textarea',
          limit: 60,
          placeholder: '60字以内で入力',
          rubric: [
            criterion('Vソフトのデータファイル', [['Vソフト', 'データファイル']]),
            criterion('読込み後1分以内', [['読み込', '1分以内']]),
            criterion('同一パス名', [['パス名', '同一']]),
            criterion('上書き', [['上書き']])
          ]
        })
      ]
    },
    {
      title: '設問4　秘密ファイルの流出',
      description: '表6及び本文の空欄f〜mを、実際の空欄ごとに入力します。',
      fields: [
        answerField('r4a-pm2q2-s10', '(1) f（ログの項目名）', 1, '添付ファイルの名称'),
        answerField('r4a-pm2q2-s11', '(1) g（ログの項目名）', 1, '添付ファイルのサイズ'),
        answerField('r4a-pm2q2-s12', '(2) h（字句）', 1, 'サイズ'),
        answerField('r4a-pm2q2-s13', '(3) i（ログの項目名）', 1, 'アップロードされたファイルのサイズ'),
        answerField('r4a-pm2q2-s14', '(3) j（ログの項目名）', 1, 'アクセス先のURL'),
        answerField('r4a-pm2q2-s15', '(4) k（字句）', 1, 'ファイル圧縮', { limit: 10, placeholder: '10字以内で入力' }),
        answerField('r4a-pm2q2-s16', '(4) l（字句）', 1, 'ファイル名', { limit: 10, placeholder: '10字以内で入力' }),
        answerField('r4a-pm2q2-s17', '(4) m（字句）', 1, 'ファイルサイズ', { limit: 10, placeholder: '10字以内で入力' })
      ]
    },
    {
      title: '設問5　再発防止の検知ルール',
      description: '下線⑤の違反操作を製品Cで検知するルールを確認します。',
      fields: [
        answerField('r4a-pm2q2-s18', '下線⑤の検知ルール', 8, '情報システム課が管理するUSB-IDのいずれにも一致しないUSB-IDのUSBメモリが装着された。', {
          type: 'textarea',
          limit: 60,
          placeholder: '60字以内で入力',
          rubric: [
            criterion('管理対象USB-IDとの不一致', [['情報システム課', '管理', 'USB-ID', '一致しない']]),
            criterion('USBメモリの装着', [['USBメモリ', '装着']])
          ]
        })
      ]
    },
    {
      title: '設問6　インシデント対応の修正',
      description: '表7の空欄n・oを、それぞれ指定字数内で答えます。',
      fields: [
        answerField('r4a-pm2q2-s19', 'n（通報窓口の見直し）', 4, '社外向けの通報窓口を設置する。', {
          type: 'textarea',
          limit: 30,
          placeholder: '30字以内で入力',
          rubric: [criterion('社外向け通報窓口の設置', [['社外向け', '通報窓口', '設置']])]
        }),
        answerField('r4a-pm2q2-s20', 'o（レベル判定の見直し）', 4, '最初の判定に加え、影響の大きさ又は影響の広がりについての事実が見つかるたびに、再判定を行う。', {
          type: 'textarea',
          limit: 50,
          placeholder: '50字以内で入力',
          rubric: [
            criterion('影響の大きさ又は広がり', [['影響', '大きさ'], ['影響', '広がり']]),
            criterion('新事実の都度再判定', [['事実', '見つかるたび', '再判定']])
          ]
        })
      ]
    }
  ];
})();
